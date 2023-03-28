import torch
import sys
from ultralytics import YOLO
import cv2
import time as t
import onnxruntime as ort
import onnx
import numpy as np
import json

if torch.cuda.is_available():
    device = "cuda:0"
    print("Using GPU")
else:
    device = "cpu"
    print("Using CPU")

modelPath = "yolov8n.pt"

yoloModel = YOLO(modelPath,task="detect")

#region Video Feed Setup
s = 0
if len(sys.argv) > 1:
    s = sys.argv[1]
source = cv2.VideoCapture(s)
win_name = 'Video Feed'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
#endregion

infTimes = 0;
numAvg = 100
while cv2.waitKey(1) != 27: # Escape
# for i in range(numAvg):
    has_frame, frame = source.read()
    if not has_frame:
        break

    startTime = t.time_ns()
    # objects = detectObjects(session,frame)
    yoloObjects = yoloModel(frame)

    for r in yoloObjects:
        for c in r.boxes.cls:
            print(yoloModel.names[int(c)])
    
    annotatedFrame = yoloObjects[0].plot()
    t1 = t.time_ns()
    # if i != 0:
        # infTimes += (t1-startTime)/1000000
    
    cv2.imshow(win_name, annotatedFrame)
    
# print(f"Avg Inference Time: {infTimes/(numAvg-1)}")

source.release()
cv2.destroyWindow(win_name)

