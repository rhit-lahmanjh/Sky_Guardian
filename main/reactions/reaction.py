from sensoryState import SensoryState
import numpy as np
# from drone import Drone
import time as t
from enum import IntEnum
from refresh_tracker import State
from yoloClasses import vision_class


### Reaction Format 
class movementReaction:

    def __init__(self) -> None:
        pass

    def react(self, input: SensoryState, currentMovement: np.array) -> np.array:
        pass

class blockingReaction:

    def __init__(self) -> None:
        pass

    def react(self, drone, input: SensoryState, currentMovement: np.array) -> None:
        pass

class definedBlockingReaction:

    def __init__(self,object: IntEnum) -> None:
        self.object = object

    def react(self, drone, input: SensoryState, currentMovement: np.array) -> None:
        pass

### Reactions where you can pass in object of interest

class followObject(movementReaction):

    def __init__(self,object: IntEnum) -> None:
        self.object = object

    def react(self, input: SensoryState, currentMovement: np.array) -> np.array:
        res = np.zeros((4,1))
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                print(f"Indicies: {int(object[5])}")
                if(int(object[5]) == int(self.object)):
                    imgWidth = input.image.shape[0]
                    res[3] = -.3*((imgWidth/2)-((object[2]+object[0])/2))
                    res[1] = (object[2]-object[0])*20/imgWidth # move back (proportional to object width)

                    # print(f'Yaw: {res[3]}')
                    print(f"Following: {int(object[5])}")
                    print(f'FOLLOW PHONE: Forward: {res[1]} Yaw: {res[3]}')
        return res


### Specific Reaction Definitions
# NOTE: the output structure of visibleObjects is an N x 6 array, [x1, y1, x2, y2, score, label]
# reacting to a specific object
class flipOnBanana(blockingReaction):

    def react(self, drone, input, currentMovement = np.zeros((4,1))):
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[5]) == vision_class.banana):
                    print('Banana Detected: Flipping')
                    drone.flip_left()

class bobOnScissors(blockingReaction):

    def react(self,drone,input, currentMovement = np.zeros((4,1))):
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[5]) == vision_class.scissors):
                    print('Shoe Detected: Bobbing')
                    drone.move_up(20)
                    t.sleep(1)
                    drone.move_down(20)
                    t.sleep(1)
                    return
                
class pauseOnSoccerBall(blockingReaction):
    def react(self,drone,input, currentMovement = np.zeros((4,1))):
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[5]) == vision_class.sports_ball):
                    drone.opstate = State.Hover
                    return

class followCellPhone(movementReaction):
    
    def react(self, input: SensoryState, currentMovement: np.array):
        res = np.zeros((4,1))
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                print(f"Indicies: {int(object[5])}")
                if(int(object[5]) == int(vision_class.cell_phone)):
                    imgWidth = input.image.shape[0]
                    res[3] = -.3*((imgWidth/2)-((object[2]+object[0])/2))
                    res[1] = (object[2]-object[0])*20/imgWidth # move back (proportional to object width)

                    # print(f'Yaw: {res[3]}')
                    print(f"Following: {int(object[5])}")
                    print(f'FOLLOW PHONE: Forward: {res[1]} Yaw: {res[3]}')
        return res
    
class runFromBanana(movementReaction):
    
    def react(self, input: SensoryState, currentMovement: np.array):
        res = np.zeros((4,1))
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[5]) == int(vision_class.banana)):
                    imgWidth = input.image.shape[0]
                    res[3] = -.3*((imgWidth/2)-((object[2]+object[0])/2))
                    res[1] = -(object[2]-object[0])*20/imgWidth # move back

                    # print(f'Yaw: {res[3]}')
                    print(f'RUN FROM SCARY BANANA: Reverse: {res[1]} Yaw: {res[3]}')
        return res

