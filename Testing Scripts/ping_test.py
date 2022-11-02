from drone import Drone
import cv2
import time as t

chuck = Drone('Chuck')

while cv2.waitKey(1) != 27: # Escape
    timeStart = t.time_ns()
    bat = chuck.get_current_state()() # swap out for any functions
    timeEnd = t.time_ns()
    print(f'battery is at :{bat.unwa} and it took {timeEnd-timeStart} ns')
