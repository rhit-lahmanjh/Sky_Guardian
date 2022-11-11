import cv2
import sys
import os
import numpy as np
import urllib
import time as t
from drone import Drone

drone1 = Drone('drone1')


source = drone1.get_frame_read()

win_name = 'Video Feed'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)

while cv2.waitKey(1) != 27: # Escape
    has_frame, frame = source.read()
    if not has_frame:
        break
    startTime = t.time_ns()
    objects = detect_objects(net,frame)
    t1 = t.time_ns()
    print(f'Inference Time: {(t1-startTime)/1000000}')
    display_objects(frame, objects,threshold=.5)
    t2= t.time_ns()
    print(f'Display Objects Time: {(t2-t1)/1000000}')
    t3=t.time_ns()
    cv2.imshow(win_name, frame)
    print(f'Display Time: {(t3-t2)/1000000}')

source.release()
cv2.destroyWindow(win_name)

