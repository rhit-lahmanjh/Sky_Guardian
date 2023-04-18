from sensoryState import SensoryState
import numpy as np
# from drone import Drone
import time as t
from enum import IntEnum
from refresh_tracker import State


### Reaction Format Interfaces
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
                if(int(object[1]) == vision_class.sports_ball):
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

class vision_class(IntEnum):
  person = 0
  bicycle = 1
  car = 2
  motorcycle = 3
  airplane = 4
  bus = 5
  train = 6
  truck = 7
  boat = 8
  traffic_light = 9
  fire_hydrant = 10
  stop_sign = 11
  parking_meter = 12
  bench = 13
  bird = 14
  cat = 15
  dog = 16
  horse = 17
  sheep = 18
  cow = 19
  elephant = 20
  bear = 21
  zebra = 22
  giraffe = 23
  backpack = 24
  umbrella = 25
  handbag = 26
  tie = 27
  suitcase = 28
  frisbee = 29
  skis = 30
  snowboard = 31
  sports_ball = 32
  kite = 33
  baseball_bat = 34
  baseball_glove = 35
  skateboard = 36
  surfboard = 37
  tennis_racket = 38
  bottle = 39
  wine_glass = 40
  cup = 41
  fork = 42
  knife = 43
  spoon = 44
  bowl = 45
  banana = 46
  apple = 47
  sandwich = 48
  orange = 49
  broccoli = 50
  carrot = 51
  hot_dog = 52
  pizza = 53
  donut = 54
  cake = 55
  chair = 56
  couch = 57
  potted_plant = 58
  bed = 59
  dining_table = 60
  toilet = 61
  tv = 62
  laptop = 63
  mouse = 64
  remote = 65
  keyboard = 66
  cell_phone = 67
  microwave = 68
  oven = 69
  toaster = 70
  sink = 71
  refrigerator = 72
  book = 73
  clock = 74
  vase = 75
  scissors = 76
  teddy_bear = 77
  hair_drier = 78
  toothbrush = 79
