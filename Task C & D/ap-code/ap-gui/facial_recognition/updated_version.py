# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'facial_recognition_screen.ui'
#
# Created by: PyQt5 UI code generator 5.15.1
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QApplication, QLabel, QVBoxLayout
from PyQt5.QtGui import QPixmap
import sys
import cv2
import os
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import numpy as np
import time
import imutils
from imutils.video import VideoStream

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)

    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):
        # setup
        name = "Hung"
        folder = "ap-code/facial-recognition/dataset/{}".format(name)

        # Create a new folder for the new name
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Get the pre-built classifier that had been trained on 3 million faces
        face_detector = cv2.CascadeClassifier("ap-code/facial-recognition/haarcascade_frontalface_default.xml")

        # capture from web cam
        # cap = cv2.VideoCapture(0)
        vs = VideoStream(src=0).start()
        # Display the Message with 3 2 1 for user
        # time.sleep(3)
        img_counter = 0
        frame_counter = 1
        while img_counter <= 10:
            
            print("Frame {}".format(frame_counter))
            # Read one frame
            # ret, frame = cam.read()
            frame = vs.read()
            frame = imutils.resize(frame, width=300, height=300)

            # Correctly flip the frame
            frame = cv2.flip(frame, -1)
            
            # Convert the color to gray
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Detect any face in the video frame
            faces = face_detector.detectMultiScale(gray, 1.3, 5)
            
            # If no face detected, continue the video capturing
            if(len(faces) == 0):
                print("No face detected, please try again")
                continue
            
            # If any face is present, show detection on frame and save images
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 128, 0), 2)
                
                # Only save images with faces every 5 frames
                # This allows better UX instead of taking 10 photos too quickly
                if frame_counter % 5 == 0:
                    # Write the image into defined dataset folder
                    img_name = "{}/{:04}.jpg".format(folder, img_counter)
                    # cv2.imwrite(img_name, frame[y : y + h, x : x + w])
                    cv2.imwrite(img_name, frame)
                    print("{} written!".format(img_name))
                    img_counter += 1
            

            # Increment the frame counter
            frame_counter += 1
            self.change_pixmap_signal.emit(frame)
        
        # Done capturing
        vs.stop()
        print("Done capturing. Transition into new window")

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self._run_flag = False
        self.wait()

class Ui_FacialRecognition(object):
    def setupUi(self, FacialRecognition):
        self.display_width = 200
        self.display_height = 200
        FacialRecognition.setObjectName("FacialRecognition")
        FacialRecognition.resize(800, 480)
        font = QtGui.QFont()
        font.setItalic(False)
        FacialRecognition.setFont(font)
        FacialRecognition.setStyleSheet("background-color: rgb(255, 255, 255);\n"
"\n"
"")
        self.centralwidget = QtWidgets.QWidget(FacialRecognition)
        self.centralwidget.setObjectName("centralwidget")
        self.logo = QtWidgets.QLabel(self.centralwidget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("../image_resources/exotic-logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.camera_feed = QtWidgets.QLabel(self.centralwidget)
        self.camera_feed.setGeometry(QtCore.QRect(250, 130, 311, 261))
        font = QtGui.QFont()
        font.setPointSize(15)
        self.camera_feed.setFont(font)
        self.camera_feed.setStyleSheet("")
        self.camera_feed.setText("")
        self.camera_feed.setPixmap(QtGui.QPixmap("../image_resources/Facial-Frame.png"))
        self.camera_feed.setScaledContents(True)
        self.camera_feed.setAlignment(QtCore.Qt.AlignCenter)
        self.camera_feed.setObjectName("camera_feed")
        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(280, 400, 241, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.label.setFont(font)
        self.label.setObjectName("label")
        FacialRecognition.setCentralWidget(self.centralwidget)
        self.statusbar = QtWidgets.QStatusBar(FacialRecognition)
        self.statusbar.setObjectName("statusbar")
        FacialRecognition.setStatusBar(self.statusbar)

        self.retranslateUi(FacialRecognition)
        QtCore.QMetaObject.connectSlotsByName(FacialRecognition)

        # Adding logic
        FacialRecognition.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.camera_feed.resize(self.display_width, self.display_height)
        # self.startCameraThread()
        
    def startCameraThread(self):
        time.sleep(5)
        self.thread = VideoThread()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        # start the thread
        self.thread.start()

    def retranslateUi(self, FacialRecognition):
        _translate = QtCore.QCoreApplication.translate
        FacialRecognition.setWindowTitle(_translate("FacialRecognition", "MainWindow"))
        self.label.setText(_translate("FacialRecognition", "Stand within the camera focal range"))

    def closeEvent(self, event):
        self.thread.stop()
        event.accept()

    # @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        self.camera_feed.setPixmap(qt_img)
    
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        p = convert_to_Qt_format.scaled(self.display_width, self.display_height, Qt.KeepAspectRatio)
        return QPixmap.fromImage(p)

if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    FacialRecognition = QtWidgets.QMainWindow()
    ui = Ui_FacialRecognition()
    ui.setupUi(FacialRecognition)
    
    FacialRecognition.show()
    
    ui.startCameraThread()
    sys.exit(app.exec_())