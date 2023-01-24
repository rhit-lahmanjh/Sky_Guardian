from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import QThread, Qt, pyqtSignal,pyqtSlot
from PyQt5 import QtGui
import djitellopy as tello
from threading import Thread
import cv2
import time as t
import sys
import numpy as np

class ourTello(tello.Tello):
    vidCap = []
    def __init__(self,name):
        super().__init__()
        self.name = name
        self.connect()
        self.streamon()
        self.vidCap = self.get_video_capture()

    def getFrame(self):
        return self.vidCap.read()

    def stop(self):
        self.vidCap.release()
        self.streamoff()
        self.end()
    
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    drone = []

    def __init__(self,drone):
        super().__init__()
        self._run_flag = True
        self.drone = drone

    def run(self):
        while self._run_flag:
            returned, cv_img = self.drone.getFrame()
            if returned:
                self.change_pixmap_signal.emit(cv_img)
    
    # shut down capture system
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class vidFeed(QWidget):
    drone = []
    image_label = []

    #constructor that takes in an individual drone, extended in the class above
    def __init__(self,drone,layout):
        super().__init__()
        self.setWindowTitle('')
        self.drone = drone
        self.display_width = 720
        self.display_height = 960
        self.textLabel = QLabel(drone.name)

        #label which contains image
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width,self.display_height)

        #assign to space in layout
        layout.addWidget(self.image_label,0,0)

        #create Thread
        self.thread = VideoThread(drone)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_image(self,cv_img):
        qt_img = self.convert_cv_qt(cv_img)
        self.image_label.setPixmap(qt_img)

    def convert_cv_qt(self,cv_img):
        rgb_image = cv2.cvtColor(cv_img,cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch*w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data,w,h,bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width,self.display_height,Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)
    
    def convert_rgb_qt(self,rgb_img):
        h, w, ch = rgb_img.shape
        bytes_per_line = ch*w
        convert_to_Qt_format = QtGui.QImage(rgb_img.data,w,h,bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width,self.display_height,Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()
        self.drone.stop()

# initial connection
chuck = ourTello('Chuck')

app = QApplication([])
cam_layout = QGridLayout()
win = vidFeed(chuck, cam_layout)
win.setGeometry(200,200,720,960)
win.setWindowTitle("Sky Guardian")
win.show()
app.exec()