import torch
import sys
from ultralytics import YOLO
import cv2
import time as t
import onnxruntime as ort
import onnx
import numpy as np
import json


# #making class dictionary
# model = YOLO("yolov8m.pt")
# res = model.predict(stream = True, imgsz = 640)
# print(model.names)

# with open('CV_testing\yolo_class_labels.txt', 'w') as f:
#     for key,value in model.names.items():
#         f.write(value + '\n')

img = cv2.imread("CV_testing\_red.jpg")

# Text Parameters
FONTFACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
THICKNESS = 1

objectClassFile = "CV_testing/yolo_class_labels.txt"

with open(objectClassFile) as fp:
    objectLabels = fp.read().split("\n")

if torch.cuda.is_available():
    device = "cuda:0"
    print("Using GPU")
else:
    device = "cpu"
    print("Using CPU")
device = "cpu"

modelPath = "yolov8m.onnx"

model = onnx.load(modelPath)
output = model.graph.output
input_all = [node.name for node in model.graph.input]
input_initializer = [node.name for node in model.graph.initializer]
net_feed_input = list(set(input_all)-set(input_initializer))
print(f"Inputs: {net_feed_input}")
# print(f"Outputs: {output}")

session = ort.InferenceSession(modelPath,providers=['CUDAExecutionProvider','CPUExecutionProvider'])
io_binding = session.io_binding()


def processOutput(yoloOutput,yoloInputImageSize = 640):

    conf_threshold = 0.8
    scores = np.max(yoloOutput[:,4:],axis=1) #highest confidence
    seenObjects = yoloOutput[scores > conf_threshold,:] #list of seenObjects

    scoresForSeenObjects= scores[scores > conf_threshold]

    # Get the class with the highest confidence
    class_ids = np.argmax(seenObjects[:, 4:], axis=1)

    # Get bounding boxes for each object
    boxes = seenObjects[:, :4]

    #rescale box
    scaling_factor = 1/yoloInputImageSize
    boxes *= scaling_factor
    # boxes = boxes.astype(np.int32)

    if np.max(scores) > conf_threshold:
        print("Found Something")

    if seenObjects.shape[0] > 0:
        transformedOutput = np.zeros((seenObjects.shape[0],6))
        transformedOutput[:,0] = class_ids
        transformedOutput[:,1] = scores[scores > conf_threshold]
        transformedOutput[:,2:] = boxes
        # transformedOutput = saveUniqueDetections(transformedOutput)
        return True, transformedOutput
    else:
        return False, None
    
def saveUniqueDetections(seenObjects):
    keepObjects = np.atleast_2d(seenObjects[0,:])
    index = 1
    for object in seenObjects:
        for object2 in keepObjects:
            if calculateIOU(object, object2)<.8:
                keepObjects[index,:] = object2
    print(keepObjects)             
    return keepObjects
        
def calculateIOU(object1, object2):
    ob1_x1 = object1[2]
    ob1_y1 = object1[3]
    ob1_x2 = object1[4]
    ob1_y2 = object1[5]

    ob2_x1 = object2[2]
    ob2_y1 = object2[3]
    ob2_x2 = object2[4]
    ob2_y2 = object2[5]

    xA = max(ob1_x1, ob2_x1)
    yA = max(ob1_y1, ob2_y1)
    xB = min(ob1_x2,ob2_x2)
    yB = min(ob1_y2,ob2_y2)

    intersectionArea = abs(xB-xA) * abs(yB-yA)

    ob1Area = (ob1_x2-ob1_x1)*(ob1_y2-ob1_y1)
    ob2Area = (ob2_x2-ob2_x1)*(ob2_y2-ob2_y1)

    iou = intersectionArea/(ob1Area+ob2Area)
    return iou

    
def outline_yolo_objects_on_image(im,objectsToOutline):
    height = im.shape[0] 
    width = im.shape[1]

    #loop through all objects
    for object in objectsToOutline:
        # class and confidence
        classId = int(object[0])
        print(f"I am seeing a {objectLabels[classId]}")
        # score = float(object[2])

        # classId = int(object[0,0,i,1])
        # score = float(object[0,0,i,2])

        # Recover original cordinates from normalized coordinates
        x1 = int(object[2] * width)
        y1 = int(object[3] * height)
        x2 = int(object[4] * width)
        y2 = int(object[5] * height)
        
        __display_text__(im, f"{objectLabels[classId]}",x1,y1)
        cv2.rectangle(im,(x1,y1),(x2,y2),(255,0,0),2)
            # print(self.objectLabels[classId])
            # print(classId)
            # print(score)
    return im

def __display_text__(im, text, x, y):
        # Get text size 
        textSize = cv2.getTextSize(text, FONTFACE, FONT_SCALE, THICKNESS)
        dim = textSize[0]
        baseline = textSize[1]
            
        # Use text size to create a black rectangle    
        cv2.rectangle(im, (x,y-dim[1] - baseline), (x + dim[0], y + baseline), (0,0,0), cv2.FILLED);

        # Display text inside the rectangle
        cv2.putText(im, text, (x, y-5 ), FONTFACE, FONT_SCALE, (0, 255, 255), THICKNESS, cv2.LINE_AA)

#region Video Feed Setup
s = 0
if len(sys.argv) > 1:
    s = sys.argv[1]
source = cv2.VideoCapture(s)
win_name = 'Video Feed'
cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
#endregion

def detectObjects(session,frame):
    cnn_input_width = 640
    cnn_input_height = 640

    rgbFrame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    resizedFrame = cv2.resize(rgbFrame, (cnn_input_width,cnn_input_height),interpolation=cv2.INTER_LINEAR)
    preprocessedFrame = np.swapaxes((resizedFrame/255).astype(np.float32),axis1=0,axis2=2)
    
    io_binding.bind_cpu_input('images', np.array([preprocessedFrame]))
    io_binding.bind_output('output0')

    session.run_with_iobinding(io_binding)

    return np.squeeze(io_binding.copy_outputs_to_cpu()[0]).T



# while cv2.waitKey(1) != 27: # Escape
infTimes = 0;
numAvg = 100
for i in range(numAvg):
    has_frame, frame = source.read()
    if not has_frame:
        break

    startTime = t.time_ns()
    objects = detectObjects(session,frame)
    
    [objectsObserved,processedObjects] = processOutput(objects)
    if objectsObserved:
        frame = outline_yolo_objects_on_image(frame,processedObjects)

    t1 = t.time_ns()
    if(i != 0):
        infTimes += (t1-startTime)/1000000
    print(f'Inference Time: {(t1-startTime)/1000000}')
    #TODO Display objects
    
    # cv2.resizeWindow(win_name, 640, 480)
    cv2.imshow(win_name, frame)
    
print(f"Avg Inference Time: {infTimes/(numAvg-1)}")

source.release()
cv2.destroyWindow(win_name)

