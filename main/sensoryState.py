from collections import deque
import numpy as np
import cv2 
from video_analyzer import VideoAnalyzer
import time as t

# update dependent on pad layout
DISTANCE_BETWEEN_MISSION_PADS = 50
X_MIN_BOUNDARY = 0
X_MAX_BOUNDARY = 50
Y_MIN_BOUNDARY = 0
Y_MAX_BOUNDARY = 150
DEBUG_PRINTS = True

class SensoryState():
    globalPose = np.ones((4,1))
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
    yawShift = 0
    yawShiftSet = False
    missionPadSetID = 0;
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

    def getFrame(self):
        return self.returnedImage, self.image
        
    def update(self,currentReadings = None):
        if self.WITH_DRONE:
            for key in currentReadings:
                queue = self.sensorReadings.get(key)
                queue.append(currentReadings.get(key))
                if(len(queue) > 10):
                    queue.popleft()
            padID = currentReadings.get('mid')
            if(padID > 0):
                if not self.yawShiftSet:
                    self.yawShift = currentReadings.get('yaw')
                    self.yawShiftSet = True
                self.globalPose[0] = currentReadings.get('x') + self.missionPadShift[padID-1,0]
                self.globalPose[1] = currentReadings.get('y') + self.missionPadShift[padID-1,1]
                self.globalPose[2] = currentReadings.get('z')
                self.globalPose[3] = currentReadings.get('yaw') - self.yawShift
            if DEBUG_PRINTS:
                print(f"Pad: {padID} X: {self.globalPose[0]} Y: {self.globalPose[1]} Z: {self.globalPose[2]} YAW : {self.globalPose[3]}")
                # print(f"Shifting by: {self.missionPadShift[padID-1,:]}")
        if self.videoCapture != None:
            self.__clearBuffer__(self.videoCapture)
            self.returnedImage, self.image = self.videoCapture.retrieve()
            if self.returnedImage:
                [self.visibleObjects,self.image] = self.videoAnalyzer.detectObjects(self.image)

    def __clearBuffer__(self, cap):
        """ Emptying buffer frame """
        while True:
            start_time = t.time()
            cap.grab()
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
