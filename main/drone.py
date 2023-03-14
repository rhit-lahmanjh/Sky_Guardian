import sys
import time

import djitellopy as tel
from perlin_noise import PerlinNoise
import cv2
import keyboard as key
import time as t
from collections import deque
import numpy as np
import math
import random as rand
import sensoryState
from behaviors.behavior import behaviorFramework
from refresh_tracker import RefreshTracker, State

DEBUG_PRINTS = True
WITH_DRONE = False
WITH_CAMERA = True
RECORD_SENSOR_STATE = True

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)
 
class Drone(tel.Tello):
    #video I THINK THIS IS DEPRICATED
    # vidCap = None
    # vision = None

    #movement
    MAXSPEED = 20
    opState = None
    prevState = None
    hoverDebounce = 0
    landDebonce = 0
    noiseGenerator = None
    xyNoiseStorage = .5
    thetaStorage = .1
    STOP = np.array([0.0,0.0,0.0,0.0])
    prevDirection = None
    wanderCounter = 20
    randomWanderVec = np.zeros((4,1))

    behavior: behaviorFramework = None

    #sensor Data
    sensoryState = None
    telemetry = dict()
    telemetryReason = dict()
    refreshTracker = None

    def __init__(self,identifier = None, behavior: behaviorFramework = None):
        cv2.VideoCapture()
        self.identifier = identifier
        self.opState = State.Grounded
        if behavior is not None:
            self.behavior = behavior
        if WITH_DRONE:
            super().__init__()
            # This is where we will implement connecting to a drone through the router
            self.connect()
            self.set_speed(self.MAXSPEED)
            self.enable_mission_pads()

            #setup video
            if WITH_CAMERA:
                self.streamon()
                self.sensoryState = sensoryState.SensoryState(self.get_current_state(),self.get_video_capture())
            else:
                self.sensoryState = sensoryState.SensoryState(self.get_current_state())
        elif not WITH_DRONE and WITH_CAMERA:
            self.sensoryState = sensoryState.SensoryState()
            self.sensoryState.setupWebcam()
            print('setup')
        else:
            self.sensoryState = sensoryState.SensoryState()

        #setup useful classes
        self.noiseGenerator = PerlinNoise(octaves=1, seed=7)
        self.refreshTracker = RefreshTracker()

    #region INTERNAL UTILITY FUNCTIONS
    def __randomWander__(self):
        if self.wanderCounter >= 5:
            while(True):
                notZeroPlease = rand.randint(-10,10)
                if(notZeroPlease != 0):
                    break
            self.xyNoiseStorage = 1/notZeroPlease
            self.wanderCounter = 0
        else:
            self.xyNoiseStorage = self.noiseGenerator(self.xyNoiseStorage)

        # print(f"Noise: {self.xyNoiseStorage}")
        self.thetaStorage = clamp(n=(self.thetaStorage + (math.pi * self.xyNoiseStorage)),minn=-math.pi/2,maxn=math.pi/2)
        # print(f"Theta: {self.thetaStorage}")
        
        xDir = math.sin(self.thetaStorage)
        yDir = math.cos(self.thetaStorage)

        newDirection = np.array([[xDir],[yDir],[0],[xDir]]) # this is not default argument bc using self

        movementVec = newDirection*self.MAXSPEED
        # print(f'Sum {movementVec}')
        self.prevDirection = movementVec
        self.wanderCounter += 1
        return self.prevDirection

    def __randomWander_simplified__(self):
        if self.wanderCounter >= 20:
            self.randomWanderVec[0] = rand.randint(-10,10)
            self.randomWanderVec[1] = rand.randint(-5,12)
            # self.randomWanderVec[3] = rand.randint(-15,15)
            self.wanderCounter = 0

        self.wanderCounter += 1
        return self.randomWanderVec

    def __avoidBoundary__(self):
        xBoundaryForceDroneFrame = 0
        yBoundaryForceDroneFrame = 0
        movementForceMagnitude = 1.2
        yaw = math.radians(self.sensoryState.globalPose[3,0])
        if self.sensoryState.globalPose[0,0] < sensoryState.X_MIN_BOUNDARY:
            error = abs(self.sensoryState.globalPose[0,0]-sensoryState.X_MIN_BOUNDARY)
            xBoundaryForce = error*movementForceMagnitude
            xBoundaryForceDroneFrame = xBoundaryForce*math.cos(yaw)
            yBoundaryForceDroneFrame = xBoundaryForce*math.sin(yaw)

        elif self.sensoryState.globalPose[0,0] > sensoryState.X_MAX_BOUNDARY:
            error = abs(self.sensoryState.globalPose[0,0]-sensoryState.X_MAX_BOUNDARY)
            xBoundaryForce = -error*movementForceMagnitude
            xBoundaryForceDroneFrame = xBoundaryForce*math.cos(yaw)
            yBoundaryForceDroneFrame = xBoundaryForce*math.sin(yaw)
        if DEBUG_PRINTS:
            print(f'Avoidance Force From X boundary: X: {xBoundaryForceDroneFrame} Y: {yBoundaryForceDroneFrame} ')

        if self.sensoryState.globalPose[1,0] < sensoryState.Y_MIN_BOUNDARY:
            error = abs(self.sensoryState.globalPose[1,0]-sensoryState.Y_MIN_BOUNDARY)
            yBoundaryForce = error*movementForceMagnitude
            xBoundaryForceDroneFrame = xBoundaryForceDroneFrame - yBoundaryForce*math.sin(yaw)
            yBoundaryForceDroneFrame = yBoundaryForceDroneFrame + yBoundaryForce*math.cos(yaw)
            
        elif self.sensoryState.globalPose[1] > sensoryState.Y_MAX_BOUNDARY:
            error = abs(self.sensoryState.globalPose[1,0]-sensoryState.Y_MAX_BOUNDARY)
            yBoundaryForce = -error*movementForceMagnitude
            xBoundaryForceDroneFrame = xBoundaryForceDroneFrame - yBoundaryForce*math.sin(yaw)
            yBoundaryForceDroneFrame = yBoundaryForceDroneFrame + yBoundaryForce*math.cos(yaw)
        
        yawContribution = 0
        if yBoundaryForceDroneFrame < 0:
            yawContribution = yBoundaryForceDroneFrame
        
        res = np.array([[xBoundaryForceDroneFrame],
                         [yBoundaryForceDroneFrame],
                         [0],
                         [yawContribution],])
        if DEBUG_PRINTS:
            print(f' Total Boundary Force: X: {res[0,0]} Y: {res[1,0]}')
        return res
    
    def operatorOverride(self):
        # land interrupt
        if(key.is_pressed('l') and not self.hoverDebounce > 10):
            self.opState = State.Land
            self.hoverDebounce = 0
            return
        self.hoverDebounce += 1
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
        if key.is_pressed('d'):
            self.opState = State.Drift
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

    def moveDirection(self,direction = np.array([[0], [0], [0], [0]])):
        """Set the speed of the drone based on xyz and yaw
        direction is:
        forward/backward : x or element 1
        side to side     : y or element 2
        up and down      : z or element 3
        yaw              : turn or element 4
        """

        cmd = f'rc {np.round_(direction[0,0],1)} {np.round_(direction[1,0],1)} {np.round_(direction[2,0],1)} {np.round_(direction[3,0],1)}'
        if WITH_DRONE:
            self.send_command_without_return(cmd)
        else:
            print(cmd)

    def fullScan(self):
        self.moveDirection([0,0,0,10])

    def hover(self):
        self.send_command_with_return('stop')
    #endregion

    def checkTelemetry(self):
        # Checks the battery charge before takeoff
        if self.opState.Grounded:
            print("Battery Charge: " + str(self.sensoryState.getSensorReading("bat")))
            if self.sensoryState.getSensorReading("bat") > 30:
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
        print("Signal Strength: " + self.query_wifi_signal_noise_ratio())
        signalStrength = self.query_wifi_signal_noise_ratio()
        if signalStrength != 'ok' and signalStrength != 'okay':
            signalStrengthInt = int(signalStrength)
        if signalStrength == 'ok':
            SignalCheck = True
        elif signalStrengthInt > 25:
            SignalCheck = True
        else:
            SignalCheck = False
            self.telemetryReason["SignalStrength"] = "SNR below 25dB. Weak Connection."

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
                        "SignalStrength":SignalCheck, "pitch":pitchCheck, "roll":rollCheck,
                        "height":HeightCheck}

        print("Completed Telemetry Checks")
        print("Final Dictionary Value: " + str(self.telemetryCheck.values()))
        return all(self.telemetryCheck.values())

    def checkNoPad(self):
        self.get_mission_pad_id()


    #region TESTING
    def dronelessTest(self):
        while cv2.waitKey(20) != 27: # Escape
            t.sleep(.01)
            self.__randomWander__()

    def missionPadProofOfConcept(self):
        self.takeoff()
        t.sleep(5)
        while cv2.waitKey(20) != 27: # Escape
            t.sleep(1)
            self.operatorOverride()
            self.go_xyz_speed_mid(50,50,50,speed=50,mid=8)
            t.sleep(1)
            self.operatorOverride()
            self.go_xyz_speed_mid(50,-50,100,speed=50,mid=8)
            t.sleep(1)
            self.operatorOverride()
            self.go_xyz_speed_mid(-50,-50,50,speed=50,mid=8)
            t.sleep(1)
            self.operatorOverride()
            self.go_xyz_speed_mid(-50,50,100,speed=50,mid=8)

    def testFunction(self):
        # while cv2.waitKey(20) != 27: # Escape
        self.takeoff()
        t.sleep(2)
        self.rotate_clockwise(360)
        t.sleep(1)
        self.land()

    def manualStopping(self):
        t.sleep(3)
        self.takeoff()
        self.move_down(20)
        while(True):
            self.look()
            self.refreshTracker.update()
            if key.is_pressed('g'):
                self.moveDirection(direction=np.array([0,self.MAXSPEED,0,0])) # move forward
                while(not key.is_pressed('s')):
                    t.sleep(.00001)
                self.hover() # stop
                t.sleep(5) # Let it coast to a stop
                self.land()
                self.refreshTracker.print()
                break

    def visualStopping(self):
        t.sleep(3)
        self.takeoff()
        while(True):
            if key.is_pressed('g'):
                break
        self.moveDirection(direction=[self.MAXSPEED,0,0,0])
        while(True):
            self.look(reaction = self.stopOnCellPhone)
            if(key.is_pressed('s')):
                self.hover()
                break
        t.sleep(3) # Let it coast to a stop
        self.land()
    #endregion

    def operate(self):
        # creating window
        # if WITH_CAMERA:
        #     cv2.namedWindow('test', cv2.WINDOW_NORMAL)

        while cv2.waitKey(20) != 27: # Escape
            #sensing
            if WITH_CAMERA:
                if WITH_DRONE:
                    self.sensoryState.update(self.get_current_state())
                else:
                    self.sensoryState.update()
                # if self.sensoryState.returnedImage:
                    # cv2.imshow('test',self.sensoryState.image)

            # self.refreshTracker.update()
            # self.refreshTracker.printAVG()
            
            self.operatorOverride()

            # State Switching 
            match self.opState:
                case State.Grounded:
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
                            self.opState = State.Wander
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

                    # self.sensoryState.globalPose[0,0] = 35
                    # self.sensoryState.globalPose[1,0] = 30
                    # self.sensoryState.globalPose[3,0] = -90
                    # self.moveDirection(np.array([[0],[20],[0],[0]]))
                    # self.moveDirection(np.add(np.array([[0],[10],[0],[0]]),self.__avoidBoundary__()))
                    if(DEBUG_PRINTS):
                        print("Wandering")
                    wanderVec = np.add(self.__randomWander_simplified__(),self.__avoidBoundary__())
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
                            time.sleep(1)
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

        self.stop()
        cv2.destroyAllWindows()

#State Control
            # # Dynamic Battery Charge, Dynamic Wi-Fi SNR, Dynamic Pitch and Roll Controls

            # # If the drone breaks the max ceiling, it will lower itself below the threshold
            # if self.getSensorReading("h") > 180:
            #     print("Drone height is breaking the altitude ceiling.")
            #     self.move_down(15) # move is in cm

            # # If the drone starts to get bad SNR values, it will move backwards one foot
            # if self.query_wifi_signal_noise_ratio() < 25:
            #     print("Drone height is breaking the altitude ceiling.")
            #     self.move_back(30) # move is in cm

            # # If the drone battery gets below 12%, the drone will land
            # # Additional Battery Charge safety measure with a higher level implementation
            # # Adds diversity, in addition to Tello hardware safety features, to how battery temp is monitored
            # if self.getSensorReading("bat") < 12:
            #     print("Drone battery charge is very low. Landing...")
            #     self.land()
            #     self.opState = State.Landed

            # # If the drone pitch is too high or low in flight, it will hover for 5 seconds to reorient itself
            # if abs(self.getSensorReading("pitch")) < 45:
            #     print("Drone pitch is not level. Hovering to regain stability...")
            #     for i in range(5):
            #         self.hover()
            #         break

            # # If the drone pitch is too high or low in flight, it will hover for 5 seconds to reorient itself
            # if abs(self.getSensorReading("roll")) < 45:
            #     print("Drone roll is not level. Hovering to regain stability...")
            #     for i in range(5):
            #         self.hover()
            #         break

            # Acceleration Safety Check


    # self.sensoryState.globalPose[0,0] = 35
    # self.sensoryState.globalPose[1,0] = 30
    # self.sensoryState.globalPose[3,0] = -90
    # self.moveDirection(np.add(self.__randomWander__(),self.__avoidBoundary__()))
    # self.moveDirection(np.add(np.array([[0],[10],[0],[0]]),self.__avoidBoundary__()))