from sensoryState import SensoryState
import numpy as np
# from drone import Drone
import time as t
from enum import Enum

import sys
sys.path.append("..")
 
# importing the hello
import reactions.reaction as rxt

class behaviorFramework:

    blockingReactions = list()
    movementReactions = list()

    def __init__(self) -> None:
        pass
    
    def runReactions(self, drone = None, input: SensoryState = None, currentMovement: np.array = None):
        for reaction in self.blockingReactions:
            reaction.react(drone = drone, input = input, currentMovement = currentMovement)
        res = np.zeros((4,1))
        for reaction in self.movementReactions:
            res = res + reaction.react(input = input, currentMovement = currentMovement)
        return res

class behavior1(behaviorFramework):
    blockingReactions = [rxt.bobOnShoe()]
    movementReactions = [rxt.followCellPhone(), rxt.runFromBanana()]
