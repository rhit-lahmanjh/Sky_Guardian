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
            separateVector = self.handleDroneCollision(self.drone1.getPose(),self.drone2.getPose())
            self.drone1.swarmMovement(separateVector)
            self.drone2.swarmMovement(-separateVector)
            self.drone1.operate(exitLoop = True)
            self.drone2.operate(exitLoop = True)

    def handleDroneCollision(self,drone1Pose,drone2Pose) -> np.array((4,1)):

        # 30cm threshold
        distanceThreshold = 30
        # distance formula with drone 1 & 2 XY coordinates
        distance = math.sqrt(((x2 - x1)**2) + ((y2 - y1)**2))
        if distance < distanceThreshold:
            # invert the directional vectors on the drones to push them apart

        # KIRK outline code
        return np.zeros((4,1))