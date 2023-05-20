from drone import Drone
import numpy as np
import math
import keyboard as key
from drone_states import State
import time as t
from configparser import ConfigParser

class Swarm():

    drone1:Drone
    drone2:Drone

    turnOff = False

    def __init__(self,drone1:Drone, drone2:Drone) -> None:
        #this should later be updated to have more than 2 if time allows
        self.drone1 = drone1
        self.drone2 = drone2
        self.repo_properties = ConfigParser()
        self.repo_properties.read("main\\repo.properties")
    
    def override_drone(self,drone:Drone):
        if(key.is_pressed(self.repo_properties.get("all","D1_LAND_KEY")) and not self.drone1.recently_sent_land):
                drone.opState = State.Land
                drone.recently_sent_land = True
                return
        elif key.is_pressed(self.repo_properties.get("all","D1_HOVER_KEY")):
            if drone.prevState == None:
                drone.prevState = self.drone1.opState
                drone.opState = State.Hover
                drone.hover_debounce = t.time();
            if drone.prevState != None and (t.time() - self.drone1.hover_debounce)> 1:
                drone.opState = self.drone1.prevState
                drone.prevState = None
            return
        elif key.is_pressed(self.repo_properties.get("all","D1_WANDER_KEY")):
            drone.opState = State.Wander
            return
        elif key.is_pressed(self.repo_properties.get("all","D1_TAKEOFF_KEY")):
            drone.opState = State.Takeoff
            print("TAKEOFF")
        elif key.is_pressed(self.repo_properties.get("all","D1_DRIFT_KEY")):
            drone.opState = State.Drift

    def operator_override(self):
        if(key.is_pressed('1')):
            self.override_drone(self.drone1)
            print("DRONE 1")
        if(key.is_pressed('2')):
            self.override_drone(self.drone2)
            print("DRONE 2")

    def operate(self):
        while not self.turnOff: # Escape
            self.drone1.operate(exitLoop = True)
            # t.sleep(.2)
            self.drone2.operate(exitLoop = True)
            self.operator_override()
            # if self.drone1.getPose()[0] != 1 and self.drone2.getPose()[0] != 1:
            #     separateDroneTwoForceVector = self.handleDroneTwoCollision(self.drone1.getPose(), self.drone2.getPose())
            #     self.drone1.swarmMovement(self.drone1.transformGlobalToDroneSpace(-separateDroneTwoForceVector[0:3]))
            #     self.drone2.swarmMovement(self.drone2.transformGlobalToDroneSpace(separateDroneTwoForceVector[0:3]))

            
        self.drone1.end_flight()
        self.drone2.end_flight()

    # Pose is a np array of size (4,1), where [[xpos],[ypos],[zpos],[yaw]]
    # [0,0] = xpos, [1,0] = ypos, [2,0] = zpos
    def handle_drone_two_collision(self,drone1Pose,drone2Pose) -> np.array:
        """This function calculates the appropriate velocity vector on drone 2 based on drone 1's pose. 
        It can be flipped for the same vector on drone 1.

        Args:
            drone1Pose: np array of size (4,1), where [[xpos],[ypos],[zpos],[yaw]]
            drone2Pose: np array of size (4,1), where [[xpos],[ypos],[zpos],[yaw]]

        Returns:
            np.array: np array of size (4,1), where [[xpos],[ypos],[zpos],[yaw]]
        """
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