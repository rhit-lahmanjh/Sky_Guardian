import cv2

FONTFACE = cv2.FONT_HERSHEY_SIMPLEX
FONT_SCALE = 0.7
THICKNESS = 1

class FeedAnalyzer():
    # load and define model
    ssdNet = []

    # this structure a dictionary??
    objectModelFile = "CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29/frozen_inference_graph.pb"
    objectConfigFile = "CV_testing/models/ssd_mobilenet_v2_coco_2018_03_29.pbtxt"
    objectClassFile = "CV_testing/coco_class_labels.txt"
    objectLabels = []

    wind = []

    def __init__(self):
        
        self.setUpObjectNet()

        # win_name = 'Analyzer Feed'
        # self.wind = cv2.namedWindow(win_name, cv2.WINDOW_NORMAL)
    
    def setUpObjectNet(self):
        #read class labels
        with open(self.objectClassFile) as fp:
            self.objectLabels = fp.read().split("\n")

        #read TF network and create net object (can load different networks)
        self.ssdNet = cv2.dnn.readNetFromTensorflow(self.objectModelFile, self.objectConfigFile)

    def process(self,cv_img):
        objectsInfo = self.detect_objects(cv_img)
        self.display_objects(cv_img,objectsInfo, threshold = .8)
        # cv2.imshow(self.wind, cv_img)
        
    def detect_objects(self,im = None):
        if im is None:
            print('No image to read')
            return None

        # define frame size
        yPix = im.shape[0]
        xPix = im.shape[1]

        # Create a "Blob?" whatever that is
        blob = cv2.dnn.blobFromImage(im,1.0, size = (yPix,xPix), mean = (0,0,0), swapRB=True, crop=False)

        #Pass blob to network
        self.ssdNet.setInput(blob)

        # Perform Prediction
        objects = self.ssdNet.forward()

        return objects

    def display_text(self,im, text, x, y):
        # Get text size 
        textSize = cv2.getTextSize(text, FONTFACE, FONT_SCALE, THICKNESS)
        dim = textSize[0]
        baseline = textSize[1]
            
        # Use text size to create a black rectangle    
        cv2.rectangle(im, (x,y-dim[1] - baseline), (x + dim[0], y + baseline), (0,0,0), cv2.FILLED);

        # Display text inside the rectangle
        cv2.putText(im, text, (x, y-5 ), FONTFACE, FONT_SCALE, (0, 255, 255), THICKNESS, cv2.LINE_AA)

    def display_objects(self,im, objects, threshold = 0.80):
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
                self.display_text(im, "{}".format(self.objectLabels[classId]),x,y)
                cv2.rectangle(im,(x,y), (x+w,y+h),(255,255,255),2)
                # print(self.objectLabels[classId])
                # print(classId)
                # print(score)

