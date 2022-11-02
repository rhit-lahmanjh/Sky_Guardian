from drone import Drone
import cv2
import time as t

chuck = Drone('Chuck')

while cv2.waitKey(1) != 27: # Escape
    chuck.move_left(50)
    t.sleep(5)
    chuck.move_right(50)
    t.sleep(5)
