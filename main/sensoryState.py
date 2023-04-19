from collections import deque
import numpy as np
import cv2 
from video_analyzer import VideoAnalyzer
import time as t

# update dependent on pad layout
DISTANCE_BETWEEN_MISSION_PADS = 50
X_MIN_BOUNDARY = 50
X_MAX_BOUNDARY = 100
Y_MIN_BOUNDARY = 0
Y_MAX_BOUNDARY = 50
DEBUG_PRINTS = True

class SensoryState():
    globalPose = np.ones((4,1))
    localPose = np.ones((4,1))
    missionPadShift = np.array([[0,0],
                                [0,DISTANCE_BETWEEN_MISSION_PADS],
                                [0,2*DISTANCE_BETWEEN_MISSION_PADS],
                                [0,3*DISTANCE_BETWEEN_MISSION_PADS],
                                [DISTANCE_BETWEEN_MISSION_PADS,0],
                                [DISTANCE_BETWEEN_MISSION_PADS,DISTANCE_BETWEEN_MISSION_PADS],
                                [DISTANCE_BETWEEN_MISSION_PADS,2*DISTANCE_BETWEEN_MISSION_PADS],
                                [DISTANCE_BETWEEN_MISSION_PADS,3*DISTANCE_BETWEEN_MISSION_PADS],
                                [2*DISTANCE_BETWEEN_MISSION_PADS,0],
                                [2*DISTANCE_BETWEEN_MISSION_PADS,DISTANCE_BETWEEN_MISSION_PADS],
                                [2*DISTANCE_BETWEEN_MISSION_PADS,2*DISTANCE_BETWEEN_MISSION_PADS],
                                [2*DISTANCE_BETWEEN_MISSION_PADS,3*DISTANCE_BETWEEN_MISSION_PADS],
                                [3*DISTANCE_BETWEEN_MISSION_PADS,0],
                                [3*DISTANCE_BETWEEN_MISSION_PADS,DISTANCE_BETWEEN_MISSION_PADS],
                                [3*DISTANCE_BETWEEN_MISSION_PADS,2*DISTANCE_BETWEEN_MISSION_PADS],
                                [3*DISTANCE_BETWEEN_MISSION_PADS,3*DISTANCE_BETWEEN_MISSION_PADS],])
    missionPadSector = 0
    missionPadVisibleID = 0
    yawOffset = 0
    yawOffsetSet = False
    
    sensorReadings = dict()
    videoCapture = None
    videoAnalyzer = None
    returnedImage = False
    image = None
    visibleObjects = list()

    WITH_DRONE = False

    def __init__(self, initialReadings = None,videoCapture = None):
        if initialReadings != None:
            for key in initialReadings:
                queue = deque()
                queue.append(initialReadings.get(key))
                self.sensorReadings.update({key:queue})
            self.WITH_DRONE = True
        
        if videoCapture != None:
            self.videoCapture = videoCapture
            self.videoAnalyzer = VideoAnalyzer()

    def setupWebcam(self):
        self.videoCapture = cv2.VideoCapture(0)
        self.videoAnalyzer = VideoAnalyzer()

    def update(self,currentReadings = None):
        if self.WITH_DRONE:
            for key in currentReadings:
                queue = self.sensorReadings.get(key)
                queue.append(currentReadings.get(key))
                if(len(queue) > 10):
                    queue.popleft()

            self.__updatePose__(currentReadings=currentReadings)
            print(f"Sector: {self.missionPadSector} Pad: {self.missionPadVisibleID} X: {self.globalPose[0]} Y: {self.globalPose[1]} Z: {self.globalPose[2]} YAW : {self.globalPose[3]}")

            if DEBUG_PRINTS:
                print(f"Sector: {self.missionPadSector} Pad: {self.missionPadVisibleID} X: {self.globalPose[0]} Y: {self.globalPose[1]} Z: {self.globalPose[2]} YAW : {self.globalPose[3]}")
                # print(f"Shifting by: {self.missionPadShift[padID-1,:]}")
        if self.videoCapture != None:
            self.__clearBuffer__(self.videoCapture)
            self.returnedImage, self.image = self.videoCapture.retrieve()
            if self.returnedImage:
                [self.visibleObjects,self.image] = self.videoAnalyzer.detectObjects(self.image)

    def __updatePose__(self,currentReadings = None):

        if currentReadings != None:
            padID = currentReadings.get('mid')

            if(padID > 0):
                #initial set of yaw Offset
                if not self.yawOffsetSet:
                    self.yawOffset = currentReadings.get('yaw')
                    self.yawOffsetSet = True
                
                #update sector if mission pad has changed, before setting new local pose
                if padID != self.missionPadVisibleID:
                    self.__determineMPSector__(currentReadings)
                
                self.missionPadVisibleID = padID

                #set local pose
                self.localPose[0] = currentReadings.get('x')
                self.localPose[1] = currentReadings.get('y')
                self.localPose[2] = currentReadings.get('z')
                self.localPose[3] = currentReadings.get('yaw') - self.yawOffset

                # update global pose depending on sector and pad
                self.globalPose[0] = currentReadings.get('x') + self.missionPadShift[padID-1 + (self.missionPadSector*8),0]
                self.globalPose[1] = currentReadings.get('y') + self.missionPadShift[padID-1,1]
                self.globalPose[2] = currentReadings.get('z')
                self.globalPose[3] = currentReadings.get('yaw') - self.yawOffset

    def __determineMPSector__(self,currentReadings = None):
        newPadID = currentReadings.get('mid')
        oldPadID = self.missionPadVisibleID
        # if ID 1-4 and changes to ID 5-8, with negative x, moves from sector 1 to 0
        # if ID 5-8 and changes to ID 1-4, with positive x, moves from sector 0 to 1
        if self.localPose[0] > 0 and oldPadID > 0 and oldPadID < 5 and newPadID > 4 and newPadID < 9:
            self.missionPadSector = 1
        elif self.localPose[0] < 0 and newPadID > 0 and newPadID < 5 and oldPadID > 4 and oldPadID < 9:
            self.missionPadSector = 0

    def __clearBuffer__(self, cap):
        """ Emptying buffer frame """
        while True:
            print("buffer")
            start_time = t.time()
            grabbed = cap.grab()
            if t.time()-start_time > .02:
                break

    def getSensorReading(self,sensor, average = False):
        """Reads most recent appropriate sensor reading, either most recent value or most recent averaged value
            NOTE: mpry key is not supported, this function assumes integer values
        Args:
            sensor (str): key denoting the sensor reading requested
            average (bool, optional): _description_. Defaults to False.

        Returns:
            float: _description_
        """
        if(average):
            pastXreadings = list(self.sensorReadings.get(sensor)) #TODO UPDATE
            return sum(pastXreadings)/len(pastXreadings)
        else:
            return self.sensorReadings.get(sensor)[-1]
