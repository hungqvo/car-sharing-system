from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import imutils
from imutils.video import VideoStream
import numpy as np
import os
import cv2
import time

class CvCapturing(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    close_thread_signal = pyqtSignal(QThread)
    show_booking_signal = pyqtSignal(str)
    def __init__(self, user_dict):
        super().__init__()
        self.userId = user_dict["userId"]
        self.userName = user_dict["userName"]
    def run(self):
        # setup
        folder = "ap-code/ap-gui/facial_recognition/dataset/{}".format(self.userId)

        # Create a new folder for the new name
        if not os.path.exists(folder):
            os.makedirs(folder)

        # Get the pre-built classifier that had been trained on 3 million faces
        face_detector = cv2.CascadeClassifier("ap-code/ap-gui/facial_recognition/haarcascade_frontalface_default.xml")

        # capture from web cam
        # cap = cv2.VideoCapture(0)
        time.sleep(2)
        vs = VideoStream(src=0).start()
        # Display the Message with 3 2 1 for user
        
        img_counter = 0
        frame_counter = 1
        while img_counter <= 10:
            # Read one frame

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
                continue
            
            # If any face is present, show detection on frame and save images
            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x + w, y + h), (92, 92, 251), 2)
                
                # Only save images with faces every 5 frames
                # This allows better UX instead of taking 10 photos too quickly
                if frame_counter % 10 == 0:
                    # Write the image into defined dataset folder
                    img_name = "{}/{:04}.jpg".format(folder, img_counter)
                    cv2.imwrite(img_name, frame)
                    img_counter += 1

            # Increment the frame counter
            frame_counter += 1
            self.change_pixmap_signal.emit(frame)
        
        # Done capturing
        vs.stop()
        self.stop()
        
    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.quit()   
        self.show_booking_signal.emit(self.userId)
        self.close_thread_signal.emit(self)
             
        

    