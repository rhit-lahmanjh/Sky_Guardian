from collections import deque
import numpy as np
import cv2 
from video_analyzer import VideoAnalyzer
import time as t

# update dependent on pad layout
DISTANCE_BETWEEN_MISSION_PADS = 100
X_MIN_BOUNDARY = -50
X_MAX_BOUNDARY = 150
Y_MIN_BOUNDARY = -50
Y_MAX_BOUNDARY = 350
DEBUG_PRINTS = True

#CV Settings
CONFIDENCE_THRESHOLD = .9

class SensoryState():
    globalPose = np.ones((4,1))
    missionPadShift = np.array([[0,0],
                                [0,DISTANCE_BETWEEN_MISSION_PADS],
                                [0,2*DISTANCE_BETWEEN_MISSION_PADS],
                                [0,3*DISTANCE_BETWEEN_MISSION_PADS],
                                [DISTANCE_BETWEEN_MISSION_PADS,0],
                                [DISTANCE_BETWEEN_MISSION_PADS,DISTANCE_BETWEEN_MISSION_PADS],
                                [DISTANCE_BETWEEN_MISSION_PADS,2*DISTANCE_BETWEEN_MISSION_PADS],
                                [DISTANCE_BETWEEN_MISSION_PADS,3*DISTANCE_BETWEEN_MISSION_PADS],])
    sensorReadings = dict()
    videoCapture = None
    videoAnalyzer = None
    returnedImage = False
    image = None
    objectsVisible = None

    def __init__(self, initialReadings,videoCapture = None):
        for key in initialReadings:
            queue = deque()
            queue.append(initialReadings.get(key))
            self.sensorReadings.update({key:queue})
        
        if videoCapture != None:
            self.videoCapture = videoCapture
            self.videoAnalyzer = VideoAnalyzer()

    def update(self,currentReadings):
        for key in currentReadings:
            queue = self.sensorReadings.get(key)
            queue.append(currentReadings.get(key))
            if(len(queue) > 10):
                queue.popleft()
        padID = currentReadings.get('mid')
        if(padID > 0):
            self.globalPose[0] = currentReadings.get('x') + self.missionPadShift[padID-1,0]
            self.globalPose[1] = currentReadings.get('y') + self.missionPadShift[padID-1,1]
            self.globalPose[2] = currentReadings.get('z')
            self.globalPose[3] = currentReadings.get('yaw')
        if DEBUG_PRINTS:
            print(f"Pad: {padID} X: {self.globalPose[0]} Y: {self.globalPose[1]} Z: {self.globalPose[2]}")
            print(f"Shifting by: {self.missionPadShift[padID-1,:]}")
        if self.videoCapture != None:
            self.__clearBuffer__(self.videoCapture)
            self.returnedImage, self.image = self.videoCapture.retrieve()
            if self.returnedImage:
                self.visibleObjects = self.detect_objects(self.image)

    def __clearBuffer__(self, cap):
        """ Emptying buffer frame """
        while True:
            start_time = t.time()
            grabbed = cap.grab()
            if t.time()-start_time > .02:
                break

    def detect_objects(self,img):
        print('Seeing')

        objects = self.videoAnalyzer.detect_objects(img)

        self.videoAnalyzer.outline_objects_on_image(img, objects, threshold = CONFIDENCE_THRESHOLD)
        
        objectsSeen = list()
        for object in objects[0,0,:,:]:
            if object[2] < CONFIDENCE_THRESHOLD:
                break
            objectsSeen.append(object)
            # technically it would make sense from an efficiency standpoint to implement reactions here
            # however I don't think we're working with enough data to warrant really worrying about that

    #def printStatus(self):

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
