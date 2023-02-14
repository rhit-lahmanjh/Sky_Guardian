from sensoryState import SensoryState
import numpy as np
from drone import Drone
import time as t
from enum import Enum



### Reaction Format Interfaces
class movementReaction:

    def react(self, input: SensoryState, currentMovement: np.array) -> np.array:
        pass

class blockingReaction:

    def react(self, drone: Drone, input: SensoryState, currentMovement: np.array) -> None:
        pass

### Specific Reaction Definitions
# reacting to a specific object
class flipOnBanana(blockingReaction):

    def react(self, drone, input, currentMovement = np.zeros((4,1))):
        for object in input.objectsVisible[0,0,:,:]:
            if(object == vision_class.banana):
                print('Banana Detected: Flipping')
                drone.flip_left()

class bobOnCellPhone(blockingReaction):

    def react(self,drone,input, currentMovement = np.zeros((4,1))):
        for object in input.objectsVisible:
            if(object[0] == vision_class.banana):
                print('Banana Detected: Flipping')
                drone.move_up(20)
                t.sleep(1)
                drone.move_down(20)
                return

        # for object in input.objectsVisible[0,0,:,:]:


class followCellPhone(movementReaction):
    
    def react(self, input: SensoryState, currentMovement: np.array):
        for object in input.objectsVisible:
            if(object[0]) == vision_class.hat()


                # for object in objects[0,0,:,:]:
                #     if object[2] < .8:
                #         break
                #     if object[1] == 77:
                #         cellPhoneCounter = cellPhoneCounter + 1
                #     if object[1] == 77 and cellPhoneCounter == 2:
                #         # self.prevState = self.opState
                #         # self.opState = State.Hover
                #         # self.flip_back()
                #         print(f'Cell Phone detected. Flipping')
                #         cellPhoneCounter = 0
                #         break


class vision_class(Enum):
    unlabeled = 1
    person = 2
    bicycle = 3
    car = 4
    motorcycle = 5
    airplane = 6
    bus = 7
    train = 8
    truck = 9
    boat = 10
    traffic_light = 11
    fire_hydrant = 12
    street_sign = 13
    stop_sign = 14
    parking_meter = 15
    bench = 16
    bird = 17
    cat = 18
    dog = 19
    horse = 20
    sheep = 21
    cow = 22
    elephant = 23
    bear = 24
    zebra = 25
    giraffe = 26
    hat = 27
    backpack = 28
    umbrella = 29
    shoe = 30
    eye_glasses = 31
    handbag = 32
    tie = 33
    suitcase = 34
    frisbee = 35
    skis = 36
    snowboard = 37
    sports_ball = 38
    kite = 39
    baseball_bat = 40
    baseball_glove = 41
    skateboard = 42
    surfboard = 43
    tennis_racket = 44
    bottle = 45
    plate = 46
    wine_glass = 47
    cup = 48
    fork = 49
    knife = 50
    spoon = 51
    bowl = 52
    banana = 53
    apple = 54
    sandwich = 55
    orange = 56
    broccoli = 57
    carrot = 58
    hot_dog = 59
    pizza = 60
    donut = 61
    cake = 62
    chair = 63
    couch = 64
    potted_plant = 65
    bed = 66
    mirror = 67
    dining_table = 68
    window = 69
    desk = 70
    toilet = 71
    door = 72
    tv = 73
    laptop = 74
    mouse = 75
    remote = 76
    keyboard = 77
    cell_phone = 78
    microwave = 79
    oven = 80
    toaster = 81
    sink = 82
    refrigerator = 83
    blender = 84
    book = 85
    clock = 86
    vase = 87
    scissors = 88
    teddy_bear = 89
    hair_drier = 90
    toothbrush = 91
    hair_brush = 92