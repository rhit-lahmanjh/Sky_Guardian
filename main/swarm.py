from drone import Drone
import numpy as np
import math


class Swarm():

    drone1:Drone
    drone2:Drone

    def __init__(self,drone1:Drone,drone2:Drone) -> None:
        #this should later be updated to have more than 2 if time allows
        self.drone1 = drone1
        self.drone2 = drone2

    def operate(self):
        while True: # Escape
            separateDroneTwoForceVector = self.handleDroneTwoCollision(self.drone1.getPose(), self.drone2.getPose())
            self.drone1.swarmMovement(self.drone1.transformGlobalToDroneSpace(-separateDroneTwoForceVector))
            self.drone2.swarmMovement(self.drone2.transformGlobalToDroneSpace(separateDroneTwoForceVector))
            self.drone1.operate(exitLoop = True)
            self.drone2.operate(exitLoop = True)

    # Pose is a np array of size (4,1), where [[xpos],[ypos],[zpos],[yaw]]
    # [0,0] = xpos, [1,0] = ypos, [2,0] = zpos
    def handleDroneTwoCollision(self,drone1Pose,drone2Pose) -> np.array((4,1)):

        # 30cm threshold
        distanceThreshold = 30
        # distance formula with drone 1 & 2 XY coordinates
        distance = math.sqrt(((drone2Pose[0,0] - drone1Pose[0,0])**2) + ((drone2Pose[1,0] - drone1Pose[1,0])**2))
        if distance < distanceThreshold:
            xCord = (1 / distance) * ((drone2Pose[0, 0] - drone1Pose[0, 0]) / distance)
            yCord = (1 / distance) * ((drone2Pose[1, 0] - drone1Pose[1, 0]) / distance)
            return np.array([[xCord], [yCord], [0], [0]])

        # KIRK outline code
        return np.zeros((4,1))