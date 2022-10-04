from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QWidget, QPushButton, QGridLayout
from PyQt5.QtGui import QPixmap, QColor
from PyQt5.QtCore import QThread, Qt, pyqtSignal,pyqtSlot
from PyQt5 import QtGui
import djitellopy as tel
from threading import Thread
import cv2
import time
import sys
import numpy as np

class ourTello(tel.Tello):
    def __init__(self,name):
        super().__init__()
        self.name = name
    
class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    drone = []
    frameObj = []
    frame = []

    def __init__(self,drone):
        super().__init__()
        self._run_flag = True
        self.drone = drone
        self.frameObj = drone.get_frame_read()

    def run(self):
        while self._run_flag:
            self.frame = self.frameObj.frame # might not be necessary, i'm not sure how the background frame object stores and updates frame
            goo = self.frameObj.frame
            self.change_pixmap_signal.emit(self.frame)
        # shut down capture system

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class vidFeed(QWidget):
    drone = []

    #constructor that takes in an individual drone, extended in the class above
    def __init__(self,drone,layout):
        super().__init__()
        self.setWindowTitle('')
        self.drone = drone
        self.drone.streamon()
        self.display_width = 720
        self.display_height = 960
        self.textLabel = QLabel(drone.name)

        #label which contains image
        self.image_label = QLabel(self)
        self.image_label.resize(self.display_width,self.display_height)

        #assign to space in layout
        layout.addWidget(self.image_label,0,0)
        # layout.addWidget(self.textLabel)

        #create Thread
        self.thread = VideoThread(drone)
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.start()

    @pyqtSlot(np.ndarray)
    def update_image(self,rgb_img):
        qt_img = self.convert_rgb_qt(rgb_img)
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
        chuck.streamoff()
        chuck.end()

# initial connection
chuck = ourTello('Chuck')
# chuck.connect_to_wifi('TELLO-F28715','12345678')
chuck.connect()
chuck.streamon()
# chuck.set_wifi_credentials('TELLO-F28715', 'chuck')
# chuck.end()

frameGetter = chuck.get_frame_read()
# frame = frameGetter.frame
print('Here')

app = QApplication([])
cam_layout = QGridLayout()
win = vidFeed(chuck, cam_layout)
win.setGeometry(200,200,720,960)

win.setWindowTitle("Sky Guardian")
chuck.get_udp_video_address()

win.setLayout(cam_layout)

win.show()
app.exec()