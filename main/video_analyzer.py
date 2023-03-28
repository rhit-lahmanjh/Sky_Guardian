from ultralytics import YOLO
import torch.cuda
import os.path

class VideoAnalyzer():

    visionNet = []
    netPathList = ["yolov8n.pt", "yolov8s.pt","yolov8m.pt","yolov8l.pt","yolov8x.pt"]
    netIndex = 3

    def __init__(self):
        if torch.cuda.is_available():
            device = "cuda:0"
            print("Using GPU")
        else:
            device = "cpu"
            print("Using CPU")
        self.__loadModels__()
        self.visionNet = YOLO("yolov8m.pt")
    
    def detectObjects(self,img):
        objects = self.visionNet(img)
        img = objects[0].plot()
        return objects, img

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
