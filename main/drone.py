import djitellopy_edited
import cv2
import keyboard as key
import time as t
import numpy as np
import math
import random as rand
from sensory_state import SensoryState,MissionPadMap
from drone_states import State

from behaviors.behavior import behaviorFramework
from refresh_tracker import RefreshTracker

DEBUG_PRINTS = False
WITH_DRONE = False
WITH_CAMERA = False
RUNNING_WITH_GUI = True

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

class Drone(djitellopy_edited.Tello):

    #movement
    MAXSPEED = 20
    opState = None
    prevState = None
    hover_debounce = 0
    stop_force = np.array([0.0,0.0,0.0,0.0])
    previous_direction = None
    recently_sent_land = False
    wander_counter = 20
    lost_pad_counter = 0
    random_wander_force: np.array = None #NOTE: [x,y,z,yaw]
    swarm_force: np.array = None 
    behavior: behaviorFramework = None
    yaw_start = None #used in spinning
    spun_halfway = False
    swarm = False

    #sensor Data
    sensoryState = None
    telemetry = dict()
    telemetryReason = dict()
    refreshTracker = None

    def __init__(self,identifier = None,
                 swarm = False, 
                 behavior: behaviorFramework = None,
                 tello_ip = '192.168.10.1',
                 vs_udp_ip = '0.0.0.0',
                 vs_udp_port = 11111,
                 control_udp_port = 8889,
                 state_udp_port = 8890,
                 local_computer_IP = '0.0.0.0',):
        self.swarm = swarm
        self.random_wander_force = np.zeros((4,1))
        self.swarm_force = np.zeros((4,1))
        self.identifier = identifier
        self.opState = State.Grounded
        if behavior is not None:
            self.behavior = behavior
        if WITH_DRONE:
            super().__init__(vs_udp_ip = vs_udp_ip, vs_udp_port = vs_udp_port, control_udp_port = control_udp_port, state_udp_port = state_udp_port, host=tello_ip,local_computer_IP=local_computer_IP)

            # This is where we will implement connecting to a drone through the router
            self.connect()
            self.set_video_bitrate(djitellopy_edited.Tello.BITRATE_AUTO)
            self.set_video_resolution(djitellopy_edited.Tello.RESOLUTION_480P)

            self.set_speed(self.MAXSPEED)
            self.enable_mission_pads()

            #setup video

            if WITH_CAMERA:
                self.streamon()
                self.sensoryState = SensoryState(self.get_current_state(),self.get_video_capture())
            elif not WITH_CAMERA:
                self.sensoryState = SensoryState(self.get_current_state())
            
        elif not WITH_DRONE and WITH_CAMERA:
            self.sensoryState = SensoryState()
            self.sensoryState.setupWebcam()
            print('setup complete')
        else:
            self.sensoryState = SensoryState()

        #setup useful classes
        self.refreshTracker = RefreshTracker()

    #region UTILITY FUNCTIONS

    def __randomWander__(self):
        if self.wander_counter >= 10:
            self.random_wander_force[0] = rand.randint(-15,15)
            self.random_wander_force[1] = rand.randint(-15,15)
            self.random_wander_force[3] = rand.randint(-15,15)
            self.wanderCounter = 0

        self.wander_counter += 1
        return self.random_wander_force
    
    def change_behavior(self,new_behavior:behaviorFramework = None):
        if new_behavior is not None:
            self.behavior = new_behavior
    
    def __avoidBoundary__(self):
        movement_force_magnitude = 1.2
        global_force = np.zeros((3,1))

        yaw = -math.radians(self.sensoryState.globalPose[3,0])

        #discontinuous, forces are only applied once the drone passes the boundary
        if self.sensoryState.globalPose[0,0] < MissionPadMap.X_MIN_BOUNDARY:
            global_force[0,0] = movement_force_magnitude*(MissionPadMap.X_MIN_BOUNDARY-self.sensoryState.globalPose[0,0])
        elif self.sensoryState.globalPose[0,0] > MissionPadMap.X_MAX_BOUNDARY:
            global_force[0,0] = movement_force_magnitude*(MissionPadMap.X_MAX_BOUNDARY-self.sensoryState.globalPose[0,0])

        if self.sensoryState.globalPose[1,0] < MissionPadMap.Y_MIN_BOUNDARY:
            global_force[1,0] = movement_force_magnitude*(MissionPadMap.Y_MIN_BOUNDARY - self.sensoryState.globalPose[1,0])
        elif self.sensoryState.globalPose[1] > MissionPadMap.Y_MAX_BOUNDARY:
            global_force[1,0] = movement_force_magnitude*(MissionPadMap.Y_MAX_BOUNDARY - self.sensoryState.globalPose[1,0])
        
        res = self.transformGlobalToDroneSpace(global_force,yaw=yaw)

        if DEBUG_PRINTS:
            print(f' Total Boundary Force: X: {res[0]} Y: {res[1]}')

        return res
    
    def transformGlobalToDroneSpace(self,force:np.array((3,1)),yaw = 0):
        globalSpaceForce = force

        transformationMatrix = np.array([[math.cos(yaw),-math.sin(yaw),0],
                                         [math.sin(yaw),math.cos(yaw),0],
                                         [0,0,1],])
        
        droneSpaceForce = np.matmul(transformationMatrix,globalSpaceForce)

        res = np.zeros((4,1))
        res[0:3] = droneSpaceForce
        return res
    
    def operatorOverride(self):
        # land interrupt
        if(key.is_pressed('l') and not self.recently_sent_land):
            self.opState = State.Land
            self.recently_sent_land = True
            return
        if key.is_pressed('w'):
            self.move_forward(100)
            t.sleep(1)
        if key.is_pressed('h'):
            if self.prevState == None:
                self.prevState = self.opState
                self.opState = State.Hover
                self.hover_debounce = t.time();
            if self.prevState != None and (t.time() - self.hover_debounce)> 1:
                self.opState = self.prevState
                self.prevState = None
            return
        if key.is_pressed('r'):
            self.opState = State.Wander
            return

    def end_flight(self):
        self.stop()
        if not RUNNING_WITH_GUI:
            cv2.destroyWindow(self.identifier)
    #endregion
    #region MOVEMENT FUNCTIONS
    def stop(self): # lands, cuts stream and connection with drone
        print('Stopping')
        if self.is_flying:
            self.land()
        if(WITH_DRONE):
            self.streamoff()
            self.end()
        self.sensoryState.videoCapture.release()
    
    def getPose(self):
        return self.sensoryState.globalPose
    
    def swarmMovement(self,swarmMovementVector):
        if self.swarm:
            self.swarm_force = swarmMovementVector

    def moveDirection(self,direction = np.array([[0], [0], [0], [0]])):
        """Set the speed of the drone based on xyz and yaw
        direction is:
        left/right       : x or element 1 (right +)
        forward/backward : y or element 2 (forward +)
        up and down      : z or element 3
        yaw              : turn or element 4
        """
        if np.max(direction[0:2]) > self.MAXSPEED:
            direction = self.normalize_force(direction=direction)

        cmd = f'rc {np.round_(direction[0,0],1)} {np.round_(direction[1,0],1)} {np.round_(direction[2,0],1)} {np.round_(direction[3,0],1)}'
        if WITH_DRONE:
            self.send_command_without_return(cmd)
        else:
            print(cmd)
    
    def normalize_force(self, direction = np.array([[0], [0], [0], [0]])):
        xyNorm = np.linalg.norm(direction[0:2])
        direction[0:2] = direction[0:2]*self.MAXSPEED/xyNorm
        return direction
                
    def rotate_clockwise(self):
        self.moveDirection([0,0,0,10])

    def hover(self):
        self.send_command_with_return('stop')
    #endregion

    def checkTelemetry(self):
        # Checks the battery charge before takeoff
        if self.opState.Grounded:
            print("Battery Charge: " + str(self.sensoryState.getSensorReading("bat")))
            if self.sensoryState.getSensorReading("bat") > 25:
                BatCheck = True
            else:
                BatCheck = False
                self.telemetryReason["bat"] = "Battery requires more charging."

        if not self.opState.Grounded:
            print("Battery Charge: " + str(self.sensoryState.getSensorReading("bat")))
            if self.sensoryState.getSensorReading("bat") > 12:
                BatCheck = True
            else:
                BatCheck = False
                self.telemetryReason["bat"] = "Battery charge too low."

        # Checks the highest battery temperature before takeoff
        print("Highest Battery Temperature: " + str(self.sensoryState.getSensorReading("temph")))
        if self.sensoryState.getSensorReading("temph") < 140:
            TemphCheck = True
        else:
            TemphCheck = False
            self.telemetryReason["temph"] = "Battery temperature too high."

        # Checks the baseline low temperature before takeoff
        print("Average Battery Temperature: " + str(self.sensoryState.getSensorReading("templ")))
        if self.sensoryState.getSensorReading("templ") < 95:
            TemplCheck = True
        else:
            TemplCheck = False
            self.telemetryReason["templ"] = "Average temperature too high."

        # Turns the string SNR value into an integer
        # Checks the Wi-Fi SNR value to determine signal strength
        
        #print("Signal Strength: " + self.query_wifi_signal_noise_ratio())
        #signalStrength = self.query_wifi_signal_noise_ratio()
        #if signalStrength != 'ok' and signalStrength != 'okay':
        #    signalStrengthInt = int(signalStrength)
        #if signalStrength == 'ok':
        #    SignalCheck = True
        #elif signalStrengthInt > 25:
        #    SignalCheck = True
        #else:
        #    SignalCheck = False
        #    self.telemetryReason["SignalStrength"] = "SNR below 25dB. Weak Connection."

        # Checks to make sure the pitch is not too far off
        # If the drone is too far from 0 degrees on pitch the takeoff
        # could be unsafe
        # print("Pitch: " + str(self.sensoryState.getSensorReading("pitch")))
        pitch = abs(self.sensoryState.getSensorReading("pitch"))
        if pitch < 15:
            pitchCheck = True
        else:
            pitchCheck = False
            self.telemetryReason["pitch"] = "Pitch is off center. Unstable takeoff."

        # Checks to make sure the roll is not too far off
        # If the drone is too far from 0 degrees on roll the takeoff
        # could be unsafe
        # print("Roll: " + str(self.sensoryState.getSensorReading("roll")))
        roll = abs(self.sensoryState.getSensorReading("roll"))
        if roll < 25:
            rollCheck = True
        else:
            rollCheck = False
            self.telemetryReason["roll"] = "Roll is off center. Unstable takeoff."

        # Comment out function as needed until testing can confirm desired threshold value
        # Checks to ensure the drone is at a low enough height to ensure room during takeoff for safe ascent
        # print("Height: " + str(self.sensoryState.getSensorReading("h")))
        if self.sensoryState.getSensorReading("h") < 90:
            HeightCheck = True
        else:
            HeightCheck = False
            self.telemetryReason["h"] = "Drone is too high."

        # Dictionary of Boolean values to check through static telemetry
        self.telemetryCheck = {"bat":BatCheck, "temph":TemphCheck, "templ":TemplCheck,
                         "pitch":pitchCheck, "roll":rollCheck,
                        "height":HeightCheck}

        print("Completed Telemetry Checks")
        print("Final Dictionary Value: " + str(self.telemetryCheck.values()))
        return all(self.telemetryCheck.values())

    # def verify_mission_pad(self):
    #     if self.sensoryState.missionPadVisibleID == -1 and self.is_flying:
    #         self.prevState = self.opState
    #         self.opState = State.NoPad

    def operate(self,exitLoop = False):
        # creating window
        if WITH_CAMERA and not RUNNING_WITH_GUI:
            cv2.namedWindow(self.identifier, cv2.WINDOW_NORMAL)
        while cv2.waitKey(20) != 27: # Escape
            #sensing
            if WITH_DRONE:
                self.sensoryState.update(self.get_current_state(), name = self.identifier)
            else:
                self.sensoryState.update()
                
            if WITH_CAMERA and self.sensoryState.returnedImage and not RUNNING_WITH_GUI:
                    cv2.imshow(self.identifier,self.sensoryState.image)

            if not self.swarm:
                self.operatorOverride()

            print(f"{self.identifier}")
            self.refreshTracker.update()
            self.refreshTracker.printAVG()

            # self.verify_mission_pad()
            
            # State Switching 
            match self.opState:
                case State.Grounded:
                    if self.identifier == 'beta':
                        self.__avoidBoundary__()
                    
                    if(DEBUG_PRINTS):
                        print('Landed')
                    if key.is_pressed('t'):
                        self.opState = State.Takeoff
                        print("Attempting to take off")

                case State.Takeoff:
                    if WITH_DRONE:
                        safeToTakeOff = self.checkTelemetry()
                        if safeToTakeOff:
                            print("Telemetry Checks Successful")
                            print('Taking off') 
                            self.takeoff()
                            self.opState = State.Hover # Hover for now, eventually scanning
                        else:
                            self.opState = State.Grounded
                            print("A Telemetry threshold has been violated. Unsafe takeoff/flight conditions")
                            for dictkey, value in self.telemetryReason.items():
                                print(f"{dictkey} test failed \n Reason: {value}")
                            self.telemetryReason.clear()
                            self.telemetryCheck.clear()
                    else:
                        self.opState = State.Hover
                    
                case State.Land:
                    print("Landing")
                    if WITH_DRONE:
                        self.land()
                    self.opState = State.Grounded

                case State.Scan: 
                    if self.yaw_start == None:
                        self.yaw_start = self.sensoryState.globalPose[3] 
                    elif abs(self.yaw_start-self.sensoryState.globalPose[3]) > 20 and not self.spun_halfway:
                        self.spun_halfway = True
                    elif abs(self.yaw_start-self.sensoryState.globalPose[3]) < 20 and self.spun_halfway:
                        self.opState = State
                        self.yaw_start = None
                        self.spun_halfway = False
                    if DEBUG_PRINTS:
                        print('Scanning')
                    self.rotate_clockwise()
                    continue

                case State.Wander:
                    if(DEBUG_PRINTS):
                        print("Wandering")
                    wanderVec = np.add(self.__randomWander__(),self.__avoidBoundary__(),self.swarm_force)
                    if self.behavior is not None:
                        reactionMovement = self.behavior.runReactions(drone = self, input = self.sensoryState, currentMovement = wanderVec)
                        wanderVec = np.add(wanderVec, reactionMovement)
                    self.moveDirection(wanderVec)

                case State.Hover:
                    if WITH_DRONE:
                        self.hover()
                    else:
                        print('Hovering')

                case State.Drift:
                    if WITH_DRONE:
                        wanderVec = self.__avoidBoundary__()
                        if self.behavior is not None:
                            reactionMovement = self.behavior.runReactions(drone = self, input = self.sensoryState, currentMovement = wanderVec)
                            wanderVec = np.add(wanderVec, reactionMovement)
                        self.moveDirection(wanderVec)

                case State.NoPad:
                    if self.sensoryState.missionPadVisibleID == -1 and self.is_flying and self.lost_pad_counter <=5:
                        print(f"{self.identifier} lost mission pads")
                        print('Trying to re-acquire pad ID')
                        # Elapse 5 cycles, give the drone time to reacquire Mission Pad ID
                        self.moveDirection(self.__avoidBoundary__())
                        self.lost_pad_counter += 1
                    elif self.sensoryState.missionPadVisibleID == -1 and self.is_flying:
                        print(f"{self.identifier} could not reacquire mission pad, landing...")
                        self.opState = State.Land
                        self.lost_pad_counter = 0
                    else:
                        self.opState = self.prevState
                        print(f"{self.identifier} found mission pad")
                        self.lost_pad_counter = 0
                        return

            if exitLoop: break

