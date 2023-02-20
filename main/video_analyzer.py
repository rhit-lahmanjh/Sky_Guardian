import cv2
# import onnx
# import onnxruntime
import numpy as np


# YOLOv5 Model Thresholds
SCORE_THRESHOLD = 0.5 # filter low probability class scores
NMS_THRESHOLD = 0.45 # remove overlapping boundary boxes
CONFIDENCE_THRESHOLD = 0.45 # filters low probability detections

# Text Parameters
FONTFACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
THICKNESS = 1

class VideoAnalyzer():

    #Updated Video Analyzer file after Onnx Github Implosion

    # load and define model
    visionNet = []
    # Alternate Onnx Model loading method
    # Onnx Runtime has the potential to allow models to run faster
    # onnx_model = onnx.load('yolov5n6.onnx')
    # onnx.checker.check_model(onnx_model)

    # YOLOv5 model objectFile assignment
    # objectModelFile = "yolov5n6.onnx"

    # objectFile assignments
    objectModelFile = "CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb"
    objectConfigFile = "CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"
    objectClassFile = "CV_testing/models/coco_class_labels.txt"

    # HP Patch, absolute path references for ssdNet cv model
    # objectModelFile = "C:/Users/prestokp/PycharmProjects/Sky_Guardian/CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb"
    # objectConfigFile = "C:/Users/prestokp/PycharmProjects/Sky_Guardian/CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"
    # objectClassFile = "C:/Users/prestokp/PycharmProjects/Sky_Guardian/main/coco_class_labels.txt"

    objectLabels = []

    wind = []

    def __init__(self):

        self.setUpObjectNet()
        # win_name = 'Analyzer Feed'
        # self.wind = cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    
    def setUpObjectNet(self):
        # read class labels
        with open(self.objectClassFile) as fp:
            self.objectLabels = fp.read().split("\n")  # this is lowkey done twice currently

        # read the YoloV5 onnx model
        # self.visionNet = cv2.dnn.readNetFromONNX('yolov5n6.onnx')

        # read TF network and create net object (can load different networks)
        self.visionNet = cv2.dnn.readNetFromTensorflow(self.objectModelFile, self.objectConfigFile)

    # def process(self,cv_img):
    #     objectsInfo = self.detect_objects(cv_img)
    #     self.outline_objects_on_image(cv_img,objectsInfo, threshold = .1)
    #     # cv2.imshow(self.wind, cv_img)
        
    def detect_objects(self,im = None):
        if im is None:
            print('No image to read')
            return None

        # define frame size
        yPix = im.shape[0]
        xPix = im.shape[1]

        # Create a "Blob", Binary Large Object; Contains data in a readable raw format
        blob = cv2.dnn.blobFromImage(im,1.0, size = (yPix,xPix), mean = (0,0,0), swapRB=True, crop=False)

        #Pass blob to network
        self.visionNet.setInput(blob)

        # Perform Prediction
        objects = self.visionNet.forward()

        return objects

    def __display_text__(self,im, text, x, y):
        # Get text size 
        textSize = cv2.getTextSize(text, FONTFACE, FONT_SCALE, THICKNESS)
        dim = textSize[0]
        baseline = textSize[1]
            
        # Use text size to create a black rectangle    
        cv2.rectangle(im, (x,y-dim[1] - baseline), (x + dim[0], y + baseline), (0,0,0), cv2.FILLED);

        # Display text inside the rectangle
        cv2.putText(im, text, (x, y-5 ), FONTFACE, FONT_SCALE, (0, 255, 255), THICKNESS, cv2.LINE_AA)

    def outline_objects_on_image(self,im, objectsToOutline):
        rows = im.shape[0] 
        cols = im.shape[1]

        #loop through all objects
        for object in objectsToOutline:
            # class and confidence
            classId = int(object[1])
            # score = float(object[2])

            # classId = int(object[0,0,i,1])
            # score = float(object[0,0,i,2])

            # Recover original cordinates from normalized coordinates
            x = int(object[3] * cols)
            y = int(object[4] * rows)
            w = int(object[5] * cols - x)
            h = int(object[6] * rows - y)
            # x = int(objects[0, 0, i, 3] * cols)
            # y = int(objects[0, 0, i, 4] * rows)
            # w = int(objects[0, 0, i, 5] * cols - x)
            # h = int(objects[0, 0, i, 6] * rows - y)
            # check detection quality
            # if score > threshold:
            self.__display_text__(im, "{}".format(self.objectLabels[classId]),x,y)
            cv2.rectangle(im,(x,y), (x+w,y+h),(255,255,255),2)
                # print(self.objectLabels[classId])
                # print(classId)
                # print(score)

