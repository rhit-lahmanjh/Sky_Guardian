from drone import Drone
import numpy as np
import math
import keyboard as key
from refresh_tracker import State
import time as t


class Swarm():

    drone1:Drone
    drone2:Drone

    turnOff = False

    def __init__(self,drone1:Drone, drone2:Drone) -> None:
        #this should later be updated to have more than 2 if time allows
        self.drone1 = drone1
        self.drone2 = drone2
    
    def operator_override(self):
        #drone 1
        if(key.is_pressed('l') and not self.drone1.recently_sent_land):
            self.drone1.opState = State.Land
            self.drone1.recently_sent_land = True
            return
        elif key.is_pressed('u'):
            if self.drone1.prevState == None:
                self.drone1.prevState = self.drone1.opState
                self.drone1.opState = State.Hover
                self.drone1.hover_debounce = t.time();
            if self.drone1.prevState != None and (t.time() - self.drone1.hover_debounce)> 1:
                self.drone1.opState = self.drone1.prevState
                self.drone1.prevState = None
            return
        elif key.is_pressed('k'):
            self.drone1.opState = State.Wander
            return
        elif key.is_pressed("j"):
            self.drone1.opState = State.Takeoff
        elif key.is_pressed("e"):
            self.drone1.opState = State.Drift
        
        #drone 2
        if(key.is_pressed('s') and not self.drone2.recently_sent_land):
            self.drone2.opState = State.Land
            self.drone2.recently_sent_land = True
            return
        elif key.is_pressed('r'):
            if self.drone2.prevState == None:
                self.drone2.prevState = self.drone2.opState
                self.drone2.opState = State.Hover
                self.drone2.hover_debounce = t.time();
            if self.drone2.prevState != None and (t.time() - self.drone2.hover_debounce)> 1:
                self.drone2.opState = self.drone2.prevState
                self.drone2.prevState = None
            return
        elif key.is_pressed('d'):
            self.drone2.opState = State.Wander
            return
        elif key.is_pressed("f"):
            self.drone2.opState = State.Takeoff
        elif key.is_pressed("i"):
            self.drone2.opState = State.Drift
        
    def operate(self):
        while not self.turnOff: # Escape
            self.operator_override()
            if self.drone1.getPose()[0] != 1 and self.drone2.getPose()[0] != 1:
                separateDroneTwoForceVector = self.handleDroneTwoCollision(self.drone1.getPose(), self.drone2.getPose())
                print(f"Global: {separateDroneTwoForceVector}")

                print(f"Drone 1: {self.drone1.transformGlobalToDroneSpace(-separateDroneTwoForceVector[0:3])}")
                print(f"Drone 2: {self.drone2.transformGlobalToDroneSpace(separateDroneTwoForceVector[0:3])}")
                self.drone1.swarmMovement(self.drone1.transformGlobalToDroneSpace(-separateDroneTwoForceVector[0:3]))
                self.drone2.swarmMovement(self.drone2.transformGlobalToDroneSpace(separateDroneTwoForceVector[0:3]))
            # print(f"SSS {self.drone1.identifier} Sector: {self.drone1.sensoryState.missionPadSector} Pad: {self.drone1.sensoryState.missionPadVisibleID} X: {self.drone1.sensoryState.globalPose[0]} Y: {self.drone1.sensoryState.globalPose[1]} Z: {self.drone1.sensoryState.globalPose[2]} YAW : {self.drone1.sensoryState.globalPose[3]}")
            # print(f"SSS {self.drone2.identifier} Sector: {self.drone2.sensoryState.missionPadSector} Pad: {self.drone2.sensoryState.missionPadVisibleID} X: {self.drone2.sensoryState.globalPose[0]} Y: {self.drone2.sensoryState.globalPose[1]} Z: {self.drone2.sensoryState.globalPose[2]} YAW : {self.drone2.sensoryState.globalPose[3]}")
            self.drone1.operate(exitLoop = True)
            self.drone2.operate(exitLoop = True)
            t.sleep(.5)
        self.drone1.end_flight()
        self.drone2.end_flight()

    # Pose is a np array of size (4,1), where [[xpos],[ypos],[zpos],[yaw]]
    # [0,0] = xpos, [1,0] = ypos, [2,0] = zpos
    def handleDroneTwoCollision(self,drone1Pose,drone2Pose) -> np.array:

        # 60cm threshold
        distanceThreshold = 60
        forceMagnitude = 10
        # distance formula with drone 1 & 2 XY coordinates
        # if drone2Pose[0,0] != drone1Pose[0,0] and drone2Pose[1,0] != drone1Pose[1,0]: # NOTE TEST THIS FUNCTION
        distance = math.sqrt(((drone2Pose[0,0] - drone1Pose[0,0])**2) + ((drone2Pose[1,0] - drone1Pose[1,0])**2))
        if distance < distanceThreshold:
            xCord = (forceMagnitude *distanceThreshold/ distance) * ((drone2Pose[0, 0] - drone1Pose[0, 0]) / distance)
            yCord = (forceMagnitude *distanceThreshold/ distance) * ((drone2Pose[1, 0] - drone1Pose[1, 0]) / distance)
            return np.array([[xCord], [yCord], [0], [0]])
        else:
            return np.zeros((4,1))