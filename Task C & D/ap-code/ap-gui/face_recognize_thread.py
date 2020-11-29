from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import imutils
from imutils.video import VideoStream
import numpy as np
import os
import cv2
import time
import pickle
import face_recognition

class CvRecognizing(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    update_instruction_signal = pyqtSignal(str)
    close_thread_signal = pyqtSignal(QThread)
    def __init__(self):
        super().__init__()
        return_name = ""

    def run(self):
        # load the known faces and embeddings along with OpenCV's Haar
        # cascade for face detection
        encodings_file = "ap-code/ap-gui/facial_recognition/encodings.pickle"
        cascade_file = "ap-code/ap-gui/facial_recognition/haarcascade_frontalface_default.xml"
        data = pickle.loads(open(encodings_file, "rb").read())
        detector = cv2.CascadeClassifier(cascade_file)

        # initialize the video stream and allow the camera sensor to warm up
        vs = VideoStream(src=0).start()

        time.sleep(2.0)

        # start the FPS counter
        frame_counter = 1

        # loop over frames from the video file stream
        while frame_counter < 20:
            # grab the frame from the threaded video stream and resize it
            # to 300px (to speedup processing)
            frame = vs.read()
            frame = imutils.resize(frame, width=300, height=300)

            # Correctly flip the frame
            frame = cv2.flip(frame, -1)
            
            # convert the input frame from (1) BGR to grayscale (for face
            # detection) and (2) from BGR to RGB (for face recognition)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # detect faces in the grayscale frame
            rects = detector.detectMultiScale(gray, scaleFactor=1.1, 
                minNeighbors=5, minSize=(30, 30),
                flags=cv2.CASCADE_SCALE_IMAGE)

            # OpenCV returns bounding box coordinates in (x, y, w, h) order
            # but we need them in (top, right, bottom, left) order, so we
            # need to do a bit of reordering
            boxes = [(y, x + w, y + h, x) for (x, y, w, h) in rects]

            # compute the facial embeddings for each face bounding box
            encodings = face_recognition.face_encodings(rgb, boxes)
            names = []

            # loop over the facial embeddings
            for encoding in encodings:
                # attempt to match each face in the input image to our known
                # encodings
                matches = face_recognition.compare_faces(data["encodings"],
                    encoding)
                name = "Unknown"

                # check to see if we have found a match
                if True in matches:
                    # find the indexes of all matched faces then initialize a
                    # dictionary to count the total number of times each face
                    # was matched
                    matchedIdxs = [i for (i, b) in enumerate(matches) if b]
                    counts = {}

                    # loop over the matched indexes and maintain a count for
                    # each recognized face face
                    for i in matchedIdxs:
                        name = data["names"][i]
                        counts[name] = counts.get(name, 0) + 1

                    # determine the recognized face with the largest number
                    # of votes (note: in the event of an unlikely tie Python
                    # will select first entry in the dictionary)
                    name = max(counts, key=counts.get)
                
                # update the list of names
                names.append(name)

            # loop over the recognized faces
            for ((top, right, bottom, left), name) in zip(boxes, names):
                # draw the predicted face name on the image
                cv2.rectangle(frame, (left, top), (right, bottom),\
                    (92, 92, 251), 2)
                y = top - 15 if top - 15 > 15 else top + 15
                cv2.putText(frame, name[0:8], (left, y), cv2.FONT_HERSHEY_SIMPLEX,\
                    0.75, (92, 92, 251), 2)
                self.return_name = name
                frame_counter += 1

            # display the image to our screen
            self.change_pixmap_signal.emit(frame)

        # Done capturing
        vs.stop()
        
        # Update the UI with customer name
        self.update_instruction_signal.emit(self.return_name)
        self.stop()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.quit()
        self.close_thread_signal.emit(self)