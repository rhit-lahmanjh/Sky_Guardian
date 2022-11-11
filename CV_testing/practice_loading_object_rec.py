import cv2
import sys
import os
import numpy as np
import urllib
import matplotlib.pyplot as plt
import time as t

# load and define model
modelFile = "CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb"
configFile = "CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"
classFile = "CV_testing/coco_class_labels.txt"

#read class labels
with open(classFile) as fp:
    labels = fp.read().split("\n")
print(labels)

#read TF network and create net object (can load different networks)
net = cv2.dnn.readNetFromTensorflow(modelFile, configFile)

#define object detection function
def detect_objects(net,im = None):
    if im is None:
        print('No image to read')
        return null
    # define frame size
    yPix = im.shape[0]
    xPix = im.shape[1]

    # Create a "Blob?" whatever that is
    blob = cv2.dnn.blobFromImage(im,1.0, size = (yPix,xPix), mean = (0,0,0), swapRB=True, crop=False)

    #Pass blob to network
    net.setInput(blob)
    
    # Perform Prediction
    return net.forward()


FONTFACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
THICKNESS = 1

def display_text(im, text, x, y):
    # Get text size 
    textSize = cv2.getTextSize(text, FONTFACE, FONT_SCALE, THICKNESS)
    dim = textSize[0]
    baseline = textSize[1]
            
    # Use text size to create a black rectangle    
    cv2.rectangle(im, (x,y-dim[1] - baseline), (x + dim[0], y + baseline), (0,0,0), cv2.FILLED);
    # Display text inside the rectangle
    cv2.putText(im, text, (x, y-5 ), FONTFACE, FONT_SCALE, (0, 255, 255), THICKNESS, cv2.LINE_AA)

def display_objects(im, objects, threshold = 0.25):

    rows = im.shape[0]; cols = im.shape[1]

    #loop through all objects
    for i in range(objects.shape[2]):
        # class and confidence
        classId = int(objects[0,0,i,1])
        score = float(objects[0,0,i,2])

        # Recover original cordinates from normalized coordinates
        x = int(objects[0, 0, i, 3] * cols)
        y = int(objects[0, 0, i, 4] * rows)
        w = int(objects[0, 0, i, 5] * cols - x)
        h = int(objects[0, 0, i, 6] * rows - y)

        # check detection quality
        if score > threshold:
            display_text(im, "{}".format(labels[classId]),x,y)
            cv2.rectangle(im,(x,y), (x+w,y+h),(255,255,255),2)



s = 0
if len(sys.argv) > 1:
    s = sys.argv[1]

source = cv2.VideoCapture(s)

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


