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

    blockingReactions:list
    movementReactions:list

    def __init__(self) -> None:
        pass
    
    def runReactions(self, drone = None, input: SensoryState = None, currentMovement: np.array = None):
        for reaction in self.blockingReactions:
            reaction.react(drone = drone, input = input, currentMovement = currentMovement)
        res = np.zeros((4,1))
        for reaction in self.movementReactions:
            res = res + reaction.react(input = input, currentMovement = currentMovement)
        return res
    
    def add_reaction(self, new_blocking_reaction: rxt.blockingReaction = None, new_movement_reaction:rxt.movementReaction = None)
        if new_blocking_reaction is not None:
            self.blockingReactions.append(new_blocking_reaction)

        if new_movement_reaction is not None:
            self.movementReactions.append(new_movement_reaction)

    def remove_reaction(self, reaction_ID_to_remove):

        for reaction in self.blockingReactions:
            if reaction.identifier == reaction_ID_to_remove:
                self.blockingReactions.remove(reaction)
                
        for reaction in self.movementReactions:
            if reaction.identifier == reaction_ID_to_remove:
                self.movementReactions.remove(reaction)

class behavior1(behaviorFramework):
    blockingReactions = [rxt.bobOnScissors()]
    movementReactions = [rxt.followCellPhone(), rxt.runFromBanana()]
    