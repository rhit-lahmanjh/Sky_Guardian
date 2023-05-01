import djitellopytest
import djitellopy
from enum import Enum
import cv2
import keyboard as key
import time as t
import numpy as np
import math
import random as rand
from sensoryState import SensoryState
import sensoryState
from behaviors.behavior import behaviorFramework
from refresh_tracker import RefreshTracker, State

DEBUG_PRINTS = False
WITH_DRONE = True
WITH_CAMERA = True
RECORD_SENSOR_STATE = True

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

class Drone(djitellopytest.Tello):
    #video I THINK THIS IS DEPRICATED
    vidCap = None
    vision = None

    #movement
    MAXSPEED = 20
    opState = None
    prevState = None
    hoverDebounce = 0
    noiseGenerator = None
    xyNoiseStorage = .5
    thetaStorage = .1
    STOP = np.array([0.0,0.0,0.0,0.0])
    prevDirection = None
    recentlySentLandCommand = False
    wanderCounter = 20
    randomWanderVec = np.zeros((4,1)) #NOTE: [x,y,z,yaw]
    swarmVector = np.zeros((4,1))
    behavior: behaviorFramework = None

    #sensor Data
    sensoryState = None
    telemetry = dict()
    telemetryReason = dict()
    refreshTracker = None

    def __init__(self,identifier = None, 
                 behavior: behaviorFramework = None,
                 tello_ip = '192.168.10.1',
                 vs_udp_ip = '0.0.0.0',
                 vs_udp_port = 11111,
                 control_udp_port = 8889,
                 state_udp_port = 8890,
                 local_computer_IP = '0.0.0.0',):
        # cv2.VideoCapture()
        self.identifier = identifier
        self.opState = State.Grounded
        if behavior is not None:
            self.behavior = behavior
        if WITH_DRONE:
            super().__init__(tello_ip = tello_ip, vs_udp_ip = vs_udp_ip, vs_udp_port = vs_udp_port, control_udp_port = control_udp_port, state_udp_port = state_udp_port, host=tello_ip,local_computer_IP=local_computer_IP)

            # This is where we will implement connecting to a drone through the router
            self.connect()
            self.set_video_bitrate(djitellopytest.Tello.BITRATE_AUTO)
            # self.set_video_fps(djitellopytest.Tello.FPS_15)
            self.set_video_resolution(djitellopytest.Tello.RESOLUTION_480P)

            self.set_speed(self.MAXSPEED)
            self.enable_mission_pads()

            #setup video
            if WITH_CAMERA:
                self.streamon()
                self.sensoryState = SensoryState(self.get_current_state(),self.get_video_capture())
            else:
                self.sensoryState = SensoryState(self.get_current_state())
        elif not WITH_DRONE and WITH_CAMERA:
            self.sensoryState = SensoryState()
            self.sensoryState.setupWebcam()
            print('setup complete')
        else:
            self.sensoryState = SensoryState()

        #setup useful classes
        self.noiseGenerator = PerlinNoise(octaves=1, seed=7)
        self.refreshTracker = RefreshTracker()

    #region INTERNAL UTILITY FUNCTIONS

    def __randomWander__(self):
        if self.wanderCounter >= 10:
            self.randomWanderVec[0] = rand.randint(-15,15)
            self.randomWanderVec[1] = rand.randint(-15,15)
            self.wanderCounter = 0

        self.wanderCounter += 1
        return self.randomWanderVec
    
    def __avoidBoundary__(self):
        movementForceMagnitude = 1.2
        globalForce = np.zeros((3,1))

        yaw = -math.radians(self.sensoryState.globalPose[3,0])

        #discontinuous, forces are only applied once the drone passes the boundary
        if self.sensoryState.globalPose[0,0] < sensoryState.X_MIN_BOUNDARY:
            globalForce[0,0] = movementForceMagnitude*(sensoryState.X_MIN_BOUNDARY-self.sensoryState.globalPose[0,0])
        elif self.sensoryState.globalPose[0,0] > sensoryState.X_MAX_BOUNDARY:
            globalForce[0,0] = movementForceMagnitude*(sensoryState.X_MAX_BOUNDARY-self.sensoryState.globalPose[0,0])

        if self.sensoryState.globalPose[1,0] < sensoryState.Y_MIN_BOUNDARY:
            globalForce[1,0] = movementForceMagnitude*(sensoryState.Y_MIN_BOUNDARY - self.sensoryState.globalPose[1,0])
        elif self.sensoryState.globalPose[1] > sensoryState.Y_MAX_BOUNDARY:
            globalForce[1,0] = movementForceMagnitude*(sensoryState.Y_MAX_BOUNDARY - self.sensoryState.globalPose[1,0])
        
        res = self.transformGlobalToDroneSpace(globalForce,yaw=yaw)

        if DEBUG_PRINTS:
            print(f' Total Boundary Force: X: {res[0]} Y: {res[1]}')

        return res
    
    def transformGlobalToDroneSpace(self,force:np.array((3,1)),yaw = 0):
        globalSpaceForce = force
        # print(f"Global Space Force: {globalSpaceForce}")
        transformationMatrix = np.array([[math.cos(yaw),-math.sin(yaw),0],
                                         [math.sin(yaw),math.cos(yaw),0],
                                         [0,0,1],])
        
        droneSpaceForce = np.matmul(transformationMatrix,globalSpaceForce)
        # print(f"Drone Space Force: {droneSpaceForce}")
        res = np.zeros((4,1))
        # print(res[0:3].shape)
        # print(droneSpaceForce.shape)
        res[0:3] = droneSpaceForce
        return res
    
    def operatorOverride(self):
        # land interrupt
        if(key.is_pressed('l') and not self.recentlySentLandCommand):
            self.opState = State.Land
            self.recentlySentLandCommand = True
            return
        if key.is_pressed('w'):
            self.move_forward(100)
            t.sleep(1)
        if key.is_pressed('h'):
            if self.prevState == None:
                self.prevState = self.opState
                self.opState = State.Hover
                self.hoverDebounce = t.time();
            if self.prevState != None and (t.time() - self.hoverDebounce)> 1:
                self.opState = self.prevState
                self.prevState = None
            return
        if key.is_pressed('r'):
            self.opState = State.Wander
            return
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
        self.swarmVector = swarmMovementVector

    def moveDirection(self,direction = np.array([[0], [0], [0], [0]])):
        """Set the speed of the drone based on xyz and yaw
        direction is:
        left/right       : x or element 1 (right +)
        forward/backward : y or element 2 (forward +)
        up and down      : z or element 3
        yaw              : turn or element 4
        """
        if np.max(direction[0:2]) > self.MAXSPEED:
            direction = self.normalizeMovementVector(direction=direction)

        cmd = f'rc {np.round_(direction[0,0],1)} {np.round_(direction[1,0],1)} {np.round_(direction[2,0],1)} {np.round_(direction[3,0],1)}'
        if WITH_DRONE:
            self.send_command_without_return(cmd)
        else:
            print(cmd)
    
    def normalizeMovementVector(self, direction = np.array([[0], [0], [0], [0]])):
        xyNorm = np.linalg.norm(direction[0:2])
        direction[0:2] = direction[0:2]*self.MAXSPEED/xyNorm
        return direction
                
    def fullScan(self):
        self.moveDirection([0,0,0,10])

    def hover(self):
        self.send_command_with_return('stop')
    #endregion

    def checkTelemetry(self):
        # Checks the battery charge before takeoff
        if self.opState.Grounded:
            print("Battery Charge: " + str(self.sensoryState.getSensorReading("bat")))
            if self.sensoryState.getSensorReading("bat") > 50:
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
        print("Pitch: " + str(self.sensoryState.getSensorReading("pitch")))
        pitch = abs(self.sensoryState.getSensorReading("pitch"))
        if pitch < 15:
            pitchCheck = True
        else:
            pitchCheck = False
            self.telemetryReason["pitch"] = "Pitch is off center. Unstable takeoff."

        # Checks to make sure the roll is not too far off
        # If the drone is too far from 0 degrees on roll the takeoff
        # could be unsafe
        print("Roll: " + str(self.sensoryState.getSensorReading("roll")))
        roll = abs(self.sensoryState.getSensorReading("roll"))
        if roll < 25:
            rollCheck = True
        else:
            rollCheck = False
            self.telemetryReason["roll"] = "Roll is off center. Unstable takeoff."

        # Comment out function as needed until testing can confirm desired threshold value
        # Checks to ensure the drone is at a low enough height to ensure room during takeoff for safe ascent
        print("Height: " + str(self.sensoryState.getSensorReading("h")))
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

    def operate(self,exitLoop = False):
        # creating window
        if WITH_CAMERA:
            cv2.namedWindow(self.identifier, cv2.WINDOW_NORMAL)
        while cv2.waitKey(20) != 27: # Escape
            #sensing
            if WITH_CAMERA:
                if WITH_DRONE:
                    self.sensoryState.update(self.get_current_state())
                else:
                    self.sensoryState.update()
                if self.sensoryState.returnedImage:
                    cv2.imshow(self.identifier,self.sensoryState.image)
            # self.refreshTracker.update()
            # self.refreshTracker.printAVG()

            self.operatorOverride()

            # State Switching 
            match self.opState:
                case State.Grounded:
                    if(DEBUG_PRINTS):
                        print('Landed')
                    print(f"{self.identifier} Swarm Vector: {self.swarmVector}")
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
                            # t.sleep(2)
                            # self.move_up(20)
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
                    if(DEBUG_PRINTS):
                        print('Scanning')
                    # self.fullScan()
                    continue

                case State.Wander:
                    if(DEBUG_PRINTS):
                        print("Wandering")
                    wanderVec = np.add(self.__randomWander__(),self.__avoidBoundary__(),self.swarmVector)
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
                        self.checkNoPad()

                case State.NoPad:
                    # State when no MissionPad is detected
                    # Mission Pad ID Numbers are Integers
                    missionPadIDNumber = [1, 2, 3, 4, 5, 6, 7, 8]
                    if self.get_mission_pad_id() != missionPadIDNumber:
                        print('Mission Pads not detected')
                        print('Elapsing 10 seconds to re-acquire pad ID')
                        # Elapse 10 seconds, give the drone time to reacquire Mission Pad ID
                        for i in range(10, 0, -1):
                            missionPadIDNumber = [1, 2, 3, 4, 5, 6, 7, 8]
                            print(i)
                            t.sleep(1)
                            # Check for Mission Pad IDs inside of elapsing time
                            idNumber = self.get_mission_pad_id()
                            if idNumber == missionPadIDNumber:
                                self.opState = State.Wander
                        # Switch to Landed state after elapsed time
                        print('No Mission Pad detected. Landing...')
                        self.opState = State.Land
                    else:
                        # Mission Pad detected, switch back to Wander State
                        print('Mission Pad detected.')
                        self.opState = State.Wander
            if exitLoop: return

        self.stop()
        cv2.destroyWindow(self.identifier)
