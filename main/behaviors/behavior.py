from sensoryState import SensoryState
import numpy as np
from drone import Drone
import time as t
from enum import Enum

import sys
sys.path.append("..")
 
# importing the hello
import reactions.reaction as rxt

class behaviorFramework:

    blockingReactions = list(type=rxt.blockingReaction)
    movementReactions = list(type=rxt.movementReaction)
    
    def runReactions(self, drone: Drone, input: SensoryState, currentMovement: np.array) -> np.array():
        for reaction in self.blockingReactions:
            reaction.react(drone = drone, input = input, currentMovement = currentMovement)
        res = np.zeros((4,1))
        for reaction in self.movementReactions:
            res = res + reaction.react(input = input, currentMovement = currentMovement)
        return res

class behavior1(behaviorFramework):
    blockingReactions = [rxt.flipOnBanana, rxt.bobOnCellPhone]
    movementReactions = [rxt.followCellPhone]
