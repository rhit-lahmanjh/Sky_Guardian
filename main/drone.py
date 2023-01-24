import sys
import djitellopy as tel
from enum import Enum
from perlin_noise import PerlinNoise
from feedAnalyzer import FeedAnalyzer
import cv2
import keyboard as key
import time as t
from collections import deque
import numpy as np
import math
import random as rand

DEBUG_PRINTS = True
WITH_DRONE = True
WITH_CAMERA = True
RECORD_SENSOR_STATE = True

clamp = lambda n, minn, maxn: max(min(maxn, n), minn)

class RefreshTracker():
    refreshRateQueue = None
    lasTimeMark = None
    maxRefresh = 0
    minRefresh = 0
    NUM_STORED_POINTS = 100

    def __init__(self) -> None:
        self.refreshRateQueue = deque()
        self.lastTimeMark = t.time()
    
    def update(self):
        currentTimeMark = t.time()
        currentRate = 1/(currentTimeMark - self.lastTimeMark)
        self.refreshRateQueue.append(currentRate)
        if(len(self.refreshRateQueue) > self.NUM_STORED_POINTS):
            self.refreshRateQueue.popleft()

    def getRate(self, max = False, average = False):
        if max:
            return max(self.refreshRateQueue)
        if average:
            return np.average(self.refreshRateQueue)
        return self.refreshRateQueue[-1]

    def print(self):
        print(f"Last Refresh Rate: {self.refreshRateQueue[-1]}\nMax Refresh Rate: {np.max(self.refreshRateQueue)}\nAverage Refresh Rate: {np.average(self.refreshRateQueue)}")

class State(Enum):
    Landed = 1
    Takeoff = 2
    Wander = 3
    FollowWalkway = 4
    FollowHallway = 5
    TrackPerson = 6
    Doorway = 7
    Scan = 8
    Hover = 9

class DistanceSensor(Enum):
    Front = 1
    Right = 2
    Back = 3
    Left = 4
    
class Drone(tel.Tello):
    #video
    vidCap = None
    vision = None
    CONFIDENCE_LEVEL = .8

    #movement
    MAXSPEED = 20
    opState = None
    prevState = None
    noiseGenerator = None
    xyNoiseStorage = .5
    thetaStorage = .1
    wanderCounter = 10
    STOP = np.array([0.0,0.0,0.0,0.0])
    prevDirection = None
    recentlySentLandCommand = False

    #sensor Data
    onboardSensorState = dict()
    distanceSensorState = dict()
    telemetry = dict()
    telemetryReason = dict()
    refreshTracker = None

    def __init__(self,identifier = None):
        cv2.VideoCapture()
        super().__init__()
        self.identifier = identifier
        self.opState = State.Landed
        if WITH_DRONE:
            # This is where we will implement connecting to a drone through the router
            self.connect()
            self.set_speed(self.MAXSPEED)
            self.__initializeSensorState__()

            #setup video
            if WITH_CAMERA:
                self.streamon()
                self.vidCap = self.get_video_capture()

        #setup useful classes
        self.noiseGenerator = PerlinNoise(octaves=7, seed=7)
        self.vision = FeedAnalyzer()
        self.refreshTracker = RefreshTracker()

        #initial distance sensors
        self.__initializeDistanceSensor__()

    #region INTERNAL UTILITY FUNCTIONS
    def __clearBuffer__(self, cap):
        """ Emptying buffer frame """
        while True:
            start_time = t.time()
            grabbed = cap.grab()
            if t.time()-start_time > .02:
                break
            
    def __getFrame__(self):
        self.__clearBuffer__(self.vidCap)
        return self.vidCap.retrieve()
    
    def __randomWander__(self):
        if self.wanderCounter >= 2:
            self.xyNoiseStorage = self.noiseGenerator(self.xyNoiseStorage)
            print(f"Noise: {self.xyNoiseStorage}")
            self.thetaStorage = clamp(n=(self.thetaStorage + (math.pi/2 * self.xyNoiseStorage)),minn=-math.pi/3,maxn=math.pi/3)
            print(f"Theta: {self.thetaStorage}")
            xDir = math.sin(self.thetaStorage)
            yDir = math.cos(self.thetaStorage)

            newDirection = np.array([xDir,yDir,0,xDir]) # this is not default argument bc using self

            movementVec = newDirection*self.MAXSPEED
            self.wanderCounter = 0
            print(f'Sum {movementVec}')
            self.prevDirection = movementVec
        self.wanderCounter += 1
        return self.prevDirection
    
    def __initializeSensorState__(self):
        states = self.get_current_state()
        if(DEBUG_PRINTS):
            print(f'Sensor readings are{states}')
            print(f'Sensor readings are returning {type(states.get("bat"))}')
            print(f'Sensor key list is: {states.keys()}')
        for key in states:
            queue = deque()
            queue.append(states.get(key))
            self.onboardSensorState.update({key:queue})

    def __initializeDistanceSensor__(self): # to be completed
        for sensor in DistanceSensor:
            queue = deque()
            self.onboardSensorState.update({sensor:queue})

    def __updateSensorState__(self):
        currentStates = self.get_current_state()
        for key in currentStates:
            queue = self.onboardSensorState.get(key)
            queue.append(currentStates.get(key))
            if(len(queue) > 10):
                queue.popleft()
        # add in here to update the distance sensors

    def operatorOverride(self):
        # land interrupt
        if(key.is_pressed('l') and  not self.recentlySentLandCommand):
            self.land()
            self.opState = State.Landed
            self.recentlySentLandCommand = True
            return
        moveDist = 30
        if key.is_pressed('up'):
            self.move_up(60)
            return
        if key.is_pressed('f'):
            self.flip_back()
            return
        if key.is_pressed('down'):
            self.move_down(moveDist)
            return
        if key.is_pressed('a'):
            self.move_left(moveDist)
            return
        if key.is_pressed('d'):
            self.move_right(moveDist)
            return
        if key.is_pressed('w'):
            self.move_forward(moveDist)
            return
        if key.is_pressed('s'):
            self.move_back(moveDist)
            return
        if key.is_pressed('left'):
            self.rotate_counter_clockwise(45)
            return
        if key.is_pressed('right'):
            self.rotate_clockwise(45)
            return
        if key.is_pressed('h'):
            self.opState = State.Hover
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
        self.vidCap.release()
        self.streamoff()
        self.end()

    def moveDirection(self,direction = np.array([0, 0, 0, 0])):
        """Set the speed of the drone based on xyz and yaw
        direction is:
        forward/backward : x or element 1
        side to side     : y or element 2
        up and down      : z or element 3
        yaw              : turn or element 4
        """

        cmd = f'rc {round(direction[0],1)} {round(direction[1],1)} {round(direction[2],1)} {round(direction[3],1)}'
        self.send_command_without_return(cmd)

    def fullScan(self):
        self.moveDirection([0,0,0,10])

    def hover(self):
        self.send_command_with_return('stop')
    #endregion
    #region SENSORY FUNCTIONS

    def look(self, reactions = None):
    # get and analyze visual stimulus
        returned, img = self.__getFrame__()
        if returned:
            print('Seeing')
            objects = self.vision.detect_objects(img)
            self.vision.display_objects(img, objects,threshold=.9)
            cv2.imshow('test', img)

            objectsSeen = list()
            for object in objects[0,0,:,:]:
                if object[2] < self.CONFIDENCE_LEVEL:
                    break
                objectsSeen.append(object)
                if(reactions != None):
                    for reaction in reactions:
                        reaction(object[1])

            return objectsSeen

    def getSensorReading(self,sensor, average = False):
        """Reads most recent appropriate sensor reading, either most recent value or most recent averaged value
            NOTE: mpry key is not supported, this function assumes integer values
        Args:
            sensor (_type_): _description_
            average (bool, optional): _description_. Defaults to False.

        Returns:
            float: _description_
        """
        # if sensor in self.onboardSensorState.keys:
        if(average):
            pastXreadings = list(self.onboardSensorState.get(sensor))
            return sum(pastXreadings)/len(pastXreadings)
        else:
            return self.onboardSensorState.get(sensor)[-1]
        # elif sensor in self.distanceSensorState.keys:
        #     if(average):
        #         pastXreadings = list(self.distanceSensorState.get(sensor))
        #         return sum(pastXreadings)/len(pastXreadings)
        #     else:
        #         return self.distanceSensorState.get(sensor)[-1]

    def checkTelemetry(self):
        # Checks the battery charge before takeoff
        if self.opState.Landed:
            print("Battery Charge: " + str(self.getSensorReading("bat")))
            if self.getSensorReading("bat") > 50:
                BatCheck = True
            else:
                BatCheck = False
                self.telemetryReason["bat"] = "Battery requires more charging."

        if not self.opState.Landed:
            print("Battery Charge: " + str(self.getSensorReading("bat")))
            if self.getSensorReading("bat") > 12:
                BatCheck = True
            else:
                BatCheck = False
                self.telemetryReason["bat"] = "Battery charge too low."

        # Checks the highest battery temperature before takeoff
        print("Highest Battery Temperature: " + str(self.getSensorReading("temph")))
        if self.getSensorReading("temph") < 140:
            TemphCheck = True
        else:
            TemphCheck = False
            self.telemetryReason["temph"] = "Battery temperature too high."

        # Checks the baseline low temperature before takeoff
        print("Average Battery Temperature: " + str(self.getSensorReading("templ")))
        if self.getSensorReading("templ") < 95:
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
        print("Pitch: " + str(self.getSensorReading("pitch")))
        pitch = abs(self.getSensorReading("pitch"))
        if pitch < 30:
            pitchCheck = True
        else:
            pitchCheck = False
            self.telemetryReason["pitch"] = "Pitch is off center. Unstable takeoff."

        # Checks to make sure the roll is not too far off
        # If the drone is too far from 0 degrees on roll the takeoff
        # could be unsafe
        print("Roll: " + str(self.getSensorReading("roll")))
        roll = abs(self.getSensorReading("roll"))
        if roll < 30:
            rollCheck = True
        else:
            rollCheck = False
            self.telemetryReason["roll"] = "Roll is off center. Unstable takeoff."

        # Comment out function as needed until testing can confirm desired threshold value
        # Checks to ensure the drone is at a low enough height to ensure room during takeoff for safe ascent
        print("Height: " + str(self.getSensorReading("h")))
        if self.getSensorReading("h") < 90:
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
    #endregion
    #region REACTIONS
    def stopOnCellPhone(self, object = None):
        if(object != None and object[1] == 77):
            self.hover()

    def pauseOnPerson(self, object = None):
        # add in logic to get back to previous state
        if(object != None and object[1] == 1):
            self.prevState = self.opState
            self.opState = State.Hover
    #endregion
    #region TESTING
    def dronelessTest(self):
        while cv2.waitKey(20) != 27: # Escape
            t.sleep(.01)
            self.__randomWander__()

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
        if(WITH_DRONE):
            cv2.namedWindow('test', cv2.WINDOW_NORMAL)

        # general loop
        while cv2.waitKey(20) != 27: # Escape
            #sensing
            self.__updateSensorState__()
            self.visibleObjects = self.look()
            #reactions=list([self.pauseOnPerson,self.stopOnCellPhone])
            self.refreshTracker.update()
            # self.refreshTracker.print()
            
            self.operatorOverride()

            #State Control
            # # Dynamic Telemetry Checks to monitor while in flight, is it possible to reuse the dictionary?
            # # Dynamic Battery Charge, Dynamic Wi-Fi SNR, Dynamic Pitch and Roll Controls

            # If the drone breaks the max ceiling, it will lower itself below the threshold
            if self.getSensorReading("h") > 180:
                print("Drone height is breaking the altitude ceiling.")
                self.move_down(15) # move is in cm

            # If the drone starts to get bad SNR values, it will move backwards one foot
            if self.query_wifi_signal_noise_ratio() < 25:
                print("Drone height is breaking the altitude ceiling.")
                self.move_back(30) # move is in cm

            # If the drone battery gets below 12%, the drone will land
            # Additional Battery Charge safety measure with a higher level implementation
            # Adds diversity, in addition to Tello hardware safety features, to how battery temp is monitored
            if self.getSensorReading("bat") < 12:
                print("Drone battery charge is very low. Landing...")
                self.land()
                self.opState = State.Landed

            # If the drone pitch is too high or low in flight, it will hover for 5 seconds to reorient itself
            if abs(self.getSensorReading("pitch")) < 45:
                print("Drone pitch is not level. Hovering to regain stability...")
                for i in range(5):
                    self.hover()
                    break

            # If the drone pitch is too high or low in flight, it will hover for 5 seconds to reorient itself
            if abs(self.getSensorReading("roll")) < 45:
                print("Drone roll is not level. Hovering to regain stability...")
                for i in range(5):
                    self.hover()
                    break

            # Acceleration Safety Check

            # State Switching STILL IN DEV
            match self.opState:
                case State.Landed:
                    if(DEBUG_PRINTS):
                        print('Landed')
                    if key.is_pressed('t'):
                        self.opState = State.Takeoff
                        print("Attempting to take off")
                case State.Takeoff:
                    safeToTakeOff = self.checkTelemetry()
                    if safeToTakeOff:
                        print("Telemetry Checks Successful")
                        print('Taking off') 
                        self.takeoff()
                        self.opState = State.Hover # Hover for now, eventually scanning
                    else:
                        self.opState = State.Landed
                        print("A Telemetry threshold has been violated. Unsafe takeoff/flight conditions")
                        for dictkey, value in self.telemetryReason.items():
                            print(f"{dictkey} test failed \n Reason: {value}")
                        self.telemetryReason.clear()
                        self.telemetryCheck.clear()
                case State.Scan:
                    if(DEBUG_PRINTS):
                        print('Scanning')
                    # self.fullScan()
                    continue
                case State.Wander:
                    if(DEBUG_PRINTS):
                        print("Wandering")
                    self.moveDirection(self.__randomWander__())
                case State.Hover:
                    self.hover()      # HOVER NEEDS A GOOD DEAL MORE DESIGN SO IT CAN BE ACCESSED FROM OTHER PARTS OF THE PROGRAM
                    continue
        self.stop()
        cv2.destroyAllWindows()

drone1 = Drone(identifier = 'chuck')
drone1.operate()
# drone1.dronelessTest()
# drone1.testFunction()
