from drone import Drone
import cv2
import time as t
import json

chuck = Drone('Chuck',False)

while cv2.waitKey(1) != 27: # Escape
    timeStart = t.time_ns()
    status = chuck.get_current_state() # swap out for any functions
    timeEnd = t.time_ns()
    printDict = json.dumps(status)
    print(f'battery is at :{printDict} and it took {timeEnd-timeStart} ns')
