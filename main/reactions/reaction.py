from sensoryState import SensoryState
import numpy as np
from drone import State
import time as t
from enum import IntEnum


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
# reacting to a specific object
class flipOnBanana(blockingReaction):
    def react(self, drone, input, currentMovement = np.zeros((4,1))):
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[1]) == vision_class.banana):
                    print('Banana Detected: Flipping')
                    drone.flip_left()

class bobOnShoe(blockingReaction):
    def react(self,drone,input, currentMovement = np.zeros((4,1))):
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[1]) == vision_class.shoe):
                    print('Shoe Detected: Bobbing')
                    drone.move_up(20)
                    t.sleep(1)
                    drone.move_down(20)
                    t.sleep(1)
                    return

class pauseOnPerson(blockingReaction):
    def react(self,drone,input, currentMovement = np.zeros((4,1))):
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[1]) == vision_class.person):
                    drone.opstate = State.Hover
                    return

class followCellPhone(movementReaction):
    def react(self, input: SensoryState, currentMovement: np.array):
        res = np.zeros((4,1))
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[1]) == int(vision_class.cell_phone)):
                    imgWidth = input.image.shape[0]
                    res[3] = -.3*imgWidth*(.5-object[3])
                    print(f'FOLLOWING CELL PHONE: Yaw: {res[3]}')
        return res
    
class runFromBanana(movementReaction):
    def react(self, input: SensoryState, currentMovement: np.array):
        res = np.zeros((4,1))
        if input.visibleObjects is not None:
            for object in input.visibleObjects:
                if(int(object[1]) == int(vision_class.banana)):
                    imgWidth = input.image.shape[0]
                    res[3] = -.3*imgWidth*(.5-object[3]) # yaw
                    res[1] = -object[5]*.3 # move back (proportional to object width)
                    print(f'Reverse: {res[1]} Yaw: {res[3]}')
        return res


class vision_class(IntEnum):
    unlabeled = 0
    person = 1
    bicycle = 2
    car = 3
    motorcycle = 4
    airplane = 5
    bus = 6
    train = 7
    truck = 8
    boat = 9
    traffic_light = 10
    fire_hydrant = 11
    street_sign = 12
    stop_sign = 13
    parking_meter = 14
    bench = 15
    bird = 16
    cat = 17
    dog = 18
    horse = 19
    sheep = 20
    cow = 21
    elephant = 22
    bear = 23
    zebra = 24
    giraffe = 25
    hat = 26
    backpack = 27
    umbrella = 28
    shoe = 29
    eye_glasses = 30
    handbag = 31
    tie = 32
    suitcase = 33
    frisbee = 34
    skis = 35
    snowboard = 36
    sports_ball = 37
    kite = 38
    baseball_bat = 39
    baseball_glove = 40
    skateboard = 41
    surfboard = 42
    tennis_racket = 43
    bottle = 44
    plate = 45
    wine_glass = 46
    cup = 47
    fork = 48
    knife = 49
    spoon = 50
    bowl = 51
    banana = 52
    apple = 53
    sandwich = 54
    orange = 55
    broccoli = 56
    carrot = 57
    hot_dog = 58
    pizza = 59
    donut = 60
    cake = 61
    chair = 62
    couch = 63
    potted_plant = 64
    bed = 65
    mirror = 66
    dining_table = 67
    window = 68
    desk = 69
    toilet = 70
    door = 71
    tv = 72
    laptop = 73
    mouse = 74
    remote = 75
    keyboard = 76
    cell_phone = 77
    microwave = 78
    oven = 79
    toaster = 80
    sink = 81
    refrigerator = 82
    blender = 83
    book = 84
    clock = 85
    vase = 86
    scissors = 87
    teddy_bear = 88
    hair_drier = 89
    toothbrush = 90
    hair_brush = 91