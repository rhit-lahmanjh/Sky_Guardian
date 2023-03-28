import torch
import sys
from ultralytics import YOLO
import cv2
import time as t

if torch.cuda.is_available():
    device = "cuda:0"
    print("Using GPU")
else:
    device = "cpu"
    print("Using CPU")
device = "cpu"

model = YOLO("yolov8m.pt")
# model.eval() #Remember that you must call model.eval() to set dropout and batch normalization layers to evaluation mode before running inference. Failing to do this will yield inconsistent inference results.
# model.to(device)


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
 
    # startTime = t.time_ns()
    objects = model(frame)
    print(objects._keys)
    # t1 = t.time_ns()
    # print(f'Inference Time: {(t1-startTime)/1000000}')
    #TODO Display objects
    
    # t2= t.time_ns()
    # print(f'Display Objects Time: {(t2-t1)/1000000}')
    # t3=t.time_ns()
    cv2.imshow(win_name, frame)
    # print(f'Display Time: {(t3-t2)/1000000}')

source.release()
cv2.destroyWindow(win_name)


# #define object detection function
# def detect_objects(torchNet,im = None):
#     if im is None:
#         print('No image to read')
#         return null
#     # define frame size
#     yPix = im.shape[0]
#     xPix = im.shape[1]

#     print(f'Y: {yPix} X: {xPix}')

#     newHeight = 640
#     newWidth = 640

#     #resize
#     im = cv2.resize(im,dsize=(newHeight,newWidth),interpolation=cv2.INTER_LINEAR)
#     print(f'newY : {im.shape[0]} newX: {im.shape[1]}')

#     # Create a "Blob?" whatever that is
#     blob = cv2.dnn.blobFromImage(im,1.0, size = (yPix,xPix), mean = (0,0,0), swapRB=True, crop=False)

#     #Pass blob to network
#     netCuda.setInput(blob)
    
#     # Perform Prediction
#     return netCuda.forward()



