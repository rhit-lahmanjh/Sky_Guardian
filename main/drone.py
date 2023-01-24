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

DEBUG_PRINTS = False
WITH_DRONE = True
WITH_CAMERA = True
RECORD_SENSOR_STATE = True

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
    Explore = 3
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
    vidCap = None
    vision = None
    MAXSPEED = 60
    CONFIDENCE_LEVEL = .8
    opState = None
    prevState = None
    noise = None
    STOP = np.array([0.0,0.0,0.0,0.0])
    prevDirection = None
    firstTakeoff = True
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
        self.noise = PerlinNoise(octaves=1, seed=7)
        self.vision = FeedAnalyzer()
        self.refreshTracker = RefreshTracker()

        #initial distance sensors
        self.__initializeDistanceSensor__()

    #region internal utility functions
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
        """Shifts a random movement vector smoothly by applying Perlin noise.

        Args:
            prevDirection (_type_, optional): _description_. Defaults to None.

        Returns:
            _type_: _description_
        """
        if self.firstTakeoff: 
            self.prevDirection = np.array([0.5,.5,.5,0]) # this is not default argument bc using self
            self.firstTakeoff = False
        else:
            self.prevDirection = self.prevDirection/self.MAXSPEED

        print(f'Previous {self.prevDirection}')
        noiseVec = self.noise(self.prevDirection)
        # n1 = self.noise(self.prevDirection[0])
        # n2 = self.noise(self.prevDirection[1])
        # n3 = self.noise(self.prevDirection[2])
        # n4 = self.noise(self.prevDirection[3])
        # self.prevDirection = np.add(self.prevDirection,np.array([n1,n2,n3,n4]))
        self.prevDirection = np.add(self.prevDirection,noiseVec)

        mag = self.MAXSPEED/np.linalg.norm(self.prevDirection)
        self.prevDirection = self.prevDirection*mag
        print(f'Sum {self.prevDirection}')
        # self.prevDirection = self.prevDirection
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
    
    #endregion
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

    def avoidObstacle(self): #outline
        obstacleForce = np.zeros((1,4))
        obstacleWeight = 10
        for key,sensor in self.distanceSensorState:
            if key == DistanceSensor.Front:
                # obstacleForce[1] = -(obstacleWeight*getSensorReading(key))
                continue
            elif key == DistanceSensor.Back:
                # obstacleForce[1] = (obstacleWeight*getSensorReading(key))
                continue
            elif key == DistanceSensor.Right:
                # obstacleForce[2] = -(obstacleWeight*getSensorReading(key))
                continue
            elif key == DistanceSensor.Left:
                # obstacleForce[2] = (obstacleWeight*getSensorReading(key))
                continue
        return obstacleForce
               
    def fullScan(self):
        self.moveDirection([0,0,0,10])

    def look(self, reaction = None): 
    # get and analyze visual stimulus
        returned, img = self.__getFrame__()
        if returned:
            print('Seeing')
            objects = self.vision.detect_objects(img)
            self.vision.display_objects(img, objects,threshold=.9)
            cv2.imshow('test', img)

            objectsSeen = list()
            # initial demo IO, soon to be removed
            # should this function take in a list of reactions to different objects?
            for object in objects[0,0,:,:]:
                if object[2] < self.CONFIDENCE_LEVEL:
                    break
                if(reaction != None):
                    reaction(object)

                # if object[1] == 77:
                    cellPhoneCounter = cellPhoneCounter + 1
                # if object[1] == 77 and cellPhoneCounter == 2:
                    # self.prevState = self.opState
                    # self.opState = State.Hover
                    # self.flip_back()
                    # print(f'Cell Phone detected. Flipping')
                    # cellPhoneCounter = 0
                    # break
            return objectsSeen

    def stopOnCellPhone(self, object = None):
        if(object != None and object[1] == 77):
            self.moveDirection(self.STOP)

    def handleUserInput(self):
        # land interrupt
        if(key.is_pressed('l')):
            self.land()
            self.opState = State.Landed
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
            self.opState = State.Explore
            return
    
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

    def operate(self):
        # creating window
        if(WITH_DRONE):
            cv2.namedWindow('test', cv2.WINDOW_NORMAL)

        # general loop
        while cv2.waitKey(20) != 27: # Escape
            if DEBUG_PRINTS:
                print("looping")
            
            self.__updateSensorState__()

            # # Dynamic Telemetry Checks to monitor while in flight, is it possible to reuse the dictionary?
            # # Dynamic Battery Temp, Dynamic Battery Charge, Dynamic Wi-Fi SNR, Dynamic Pitch and Roll Controls
            # res = True
            # for key, value in telemetryCheck.items():
            #     print(key, value)
            #     # Test Boolean Value of Dictionary
            #     # Using all() + values()
            #     # Do key value pairs need to be flipped to use the all method
            #     res = all(telemetryCheck.values())
            #     if not res:
            #         self.land()
            #         self.opState = State.Landed
            #         print("A Telemetry threshold has been violated. Please review dictionary output. ")

            # objects = self.look()
            self.refreshTracker.update()
            # self.refreshTracker.print()
            
            self.handleUserInput()

            # # Dynamic Telemetry Checks to monitor while in flight, is it possible to reuse the dictionary?
            # # Dynamic Battery Charge, Dynamic Wi-Fi SNR, Dynamic Pitch and Roll Controls

            # If the drone breaks the max ceiling, it will lower itself below the threshold
            if self.getSensorReading("h") > 345:
                self.move_down(30) # move is in cm
                print("Drone height is breaking the altitude ceiling.")

            if self.query_wifi_signal_noise_ratio() < 25:
                self.move_back(20) # move is in cm
                print("Drone height is breaking the altitude ceiling.")

            if self.getSensorReading("bat") < 12:
                self.land()
                print("Drone battery charge is very low. Landing...")

            #if abs(self.getSensorReading("pitch")) < 30:


            #if abs(self.getSensorReading("roll")) < 30:


                #State Switching SIILL IN DEV
            match self.opState:
                case State.Landed:
                    # print('Landed')
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
                case State.Scan:
                    # self.fullScan()
                    continue
                case State.Explore:
                    self.moveDirection(self.__randomWander__())
                    # self.moveDirection(np.add(self.__randomWander__(),self.avoidObstacle())) # when obstacle avoidance implemented
                case State.Hover:
                    self.moveDirection(self.STOP)


        self.stop()
        cv2.destroyAllWindows()

    # Testing Functions

    def dronelessTest(self):
        while cv2.waitKey(20) != 27: # Escape
            self.__randomWander__()
    
    def testFunction(self):
        while cv2.waitKey(20) != 27: # Escape
            print(self.get_battery())

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
                self.moveDirection(direction=[0,0,0,0]) # stop
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
                self.moveDirection(direction= self.STOP)
                break
        t.sleep(3) # Let it coast to a stop
        self.land()

drone1 = Drone(identifier = 'chuck')
# drone1.operate()
drone1.manualStopping()
# drone1.takeoff()
# t.sleep(1)
# drone1.moveDirection(np.array([4.05e+1,6.606705967041363e-49,0,0]))
# t.sleep(2)
# drone1.land()


#drone1.visualStopping()
