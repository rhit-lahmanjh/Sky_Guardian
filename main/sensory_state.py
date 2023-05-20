from collections import deque
import numpy as np
import cv2 
from video_analyzer import VideoAnalyzer
import time as t
from configparser import ConfigParser

DEBUG_PRINTS = False

repo_properties = ConfigParser()
repo_properties.read("main\\repo.properties")

DISTANCE_BETWEEN_MISSION_PADS = repo_properties.getint("all","DISTANCE_BETWEEN_MISSION_PADS")

class MissionPadMap():
    X_MIN_BOUNDARY = repo_properties.getint("all","X_MIN_BOUNDARY")
    X_MAX_BOUNDARY = repo_properties.getint("all","X_MAX_BOUNDARY")
    Y_MIN_BOUNDARY = repo_properties.getint("all","Y_MIN_BOUNDARY")
    Y_MAX_BOUNDARY = repo_properties.getint("all","Y_MAX_BOUNDARY")
    
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

class SensoryState():
    globalPose:np.array = None 
    localPose:np.array = None 
    missionPadSector = 0
    missionPadVisibleID = 0
    yawOffset = 0
    yawOffsetSet = False
    
    sensorReadings: dict = None
    videoCapture:cv2.VideoCapture = None
    videoAnalyzer = None
    returnedImage = False
    image = None
    visibleObjects: list = None

    WITH_DRONE = False

    def __init__(self, initialReadings:dict = None,videoCapture:cv2.VideoCapture = None):
        self.sensorReadings = dict()
        self.globalPose = np.ones((4,1))
        self.localPose = np.ones((4,1))
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

    def update(self,currentReadings:dict = None, name:str = None):
        if self.WITH_DRONE:

            currentReadings['yaw'] = -currentReadings.pop('yaw') # this corrects the yaw to be consistent with right hand rule
            
            self.update_pose(currentReadings=currentReadings)
            
            for key in currentReadings:
                queue = self.sensorReadings.get(key)
                queue.append(currentReadings.get(key))
                if(len(queue) > 10):
                    queue.popleft()

            if DEBUG_PRINTS:
                print(f"{name} Sector: {self.missionPadSector} Pad: {self.missionPadVisibleID} X: {self.globalPose[0]} Y: {self.globalPose[1]} Z: {self.globalPose[2]} YAW : {self.globalPose[3]}")

        if self.videoCapture != None:
            self.__clearBuffer__(self.videoCapture)
            self.returnedImage, self.image = self.videoCapture.retrieve()
            if self.returnedImage:
                [self.visibleObjects,self.image] = self.videoAnalyzer.detectObjects(self.image)

    def update_pose(self,currentReadings:dict = None):
        """Determines the pose of the drone based off of it's local mission pad reading.

        Args:
            currentReadings (dict, optional): Defaults to None.
        """
        if currentReadings != None:
            newPadID = currentReadings.get('mid')

            if(newPadID > 0):
                #initial set of yaw Offset
                if not self.yawOffsetSet:
                    self.yawOffset = currentReadings.get('yaw')
                    self.yawOffsetSet = True
                
                # update sector if mission pad has changed, before setting new local pose
                if newPadID != self.missionPadVisibleID:
                    self.determine_MP_sector(currentReadings)
                
                self.missionPadVisibleID = newPadID

                #set local pose
                self.localPose[0] = currentReadings.get('x')
                self.localPose[1] = currentReadings.get('y')
                self.localPose[2] = currentReadings.get('z')
                self.localPose[3] = currentReadings.get('yaw') - self.yawOffset

                # update global pose depending on sector and pad
                self.globalPose[0] = currentReadings.get('x') + MissionPadMap.missionPadShift[newPadID-1 + (self.missionPadSector*8),0]
                self.globalPose[1] = currentReadings.get('y') + MissionPadMap.missionPadShift[newPadID-1,1]
                self.globalPose[2] = currentReadings.get('z')
                self.globalPose[3] = currentReadings.get('yaw') - self.yawOffset
            else:
                self.missionPadVisibleID = newPadID

    def determine_MP_sector(self,currentReadings:dict = None):
        newPadID = currentReadings.get('mid')
        oldPadID = self.missionPadVisibleID
        oldX = self.localPose[0,0]
        newX = currentReadings.get('x')

        # if ID 1-4 and changes to ID 5-8, with previous local negative x, current positive local x, moves from sector 1 to 0
        # if ID 5-8 and changes to ID 1-4, with previous positive local x, current negative local x moves from sector 0 to 1
        if newX > 0 and oldX < 0 and oldPadID > 0 and oldPadID < 5 and newPadID > 4 and newPadID < 9:
            self.missionPadSector = 0
            print("SWITCH FROM 1 TO 0")
        elif newX < 0 and oldX > 0 and newPadID > 0 and newPadID < 5 and oldPadID > 4 and oldPadID < 9:
            self.missionPadSector = 1
            print("SWITCH FROM 0 TO 1")

    def __clearBuffer__(self, cap:cv2.VideoCapture):
        """ Emptying buffer frame """
        while True:
            start_time = t.time()
            grabbed = cap.grab()
            if t.time()-start_time > .02:
                break

    def get_sensor_reading(self,sensor, average = False):
        """Reads most recent appropriate sensor reading, either most recent value or most recent averaged value
            NOTE: mpry key is not supported, this function assumes integer values
        Args:
            sensor (str): key denoting the sensor reading requested
            average (bool, optional): _description_. Defaults to False.

        Returns:
            float
        """
        if(average):
            pastXreadings = list(self.sensorReadings.get(sensor)) 
            return sum(pastXreadings)/len(pastXreadings)
        else:
            return self.sensorReadings.get(sensor)[-1]
