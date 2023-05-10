from ultralytics import YOLO
import torch.cuda
import os.path

CONFIDENCE_CUTOFF = .7

class VideoAnalyzer():

    visionNet: YOLO
    
    netPathList = ["yolov8n.pt", "yolov8s.pt","yolov8m.pt","yolov8l.pt","yolov8x.pt"]
    netIndex = 1
    confidenceLevel = 0
    USING_CUDA = False

    def __init__(self,conf = CONFIDENCE_CUTOFF):
        if torch.cuda.is_available():
            device = "cuda:0"
            print("Using GPU")
            self.USING_CUDA = True
        else:
            device = "cpu"
            print("Using CPU")
        self.__loadModels__()
        self.visionNet = YOLO(self.netPathList[self.netIndex-1])
        self.confidenceLevel = conf
    
    def detectObjects(self,img):
        objects = self.visionNet(img,conf=self.confidenceLevel)
        img = objects[0].plot()
        if self.USING_CUDA:
            return objects[0].boxes.boxes.cpu(), img
        else:
            return objects[0].boxes.boxes, img

    def increase_model_size(self):
        if self.netIndex == 5:
            print("Larger model does not exist")
            return
        self.netIndex += 1
        self.visionNet = YOLO(self.netPathList[self.netIndex])

    def decrease_model_size(self):
        if self.netIndex == 1:
            print("Smaller model does not exist")
            return
        self.netIndex -= 1
        self.visionNet = YOLO(self.netPathList[self.netIndex])

    def __loadModels__(self):
        for path in self.netPathList:
            if not os.path.exists(path):
                YOLO(path)