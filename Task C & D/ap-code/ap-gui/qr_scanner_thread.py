from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import imutils
from imutils.video import VideoStream
import numpy as np
import os
import cv2
import time
from imutils.video import VideoStream
from pyzbar import pyzbar
import datetime
import imutils
import time
import cv2

class CvQrScanning(QThread):
    change_pixmap_signal = pyqtSignal(np.ndarray)
    return_engineer_id_signal = pyqtSignal(str)
    def __init__(self):
        super().__init__()
        self._run_flag = True

    def run(self):   
        # initialize the video stream and allow the camera sensor to warm up
        time.sleep(2)
        vs = VideoStream(src=0).start()
        found = set()
        engineer_id = ""
        continue_scanning = True
        frame_counter = 1

        # loop over the frames from the video stream
        while continue_scanning:
            # Read frame-by-frame from the CV video capture object
            frame = vs.read()
            frame = imutils.resize(frame, width=300, height=300)
            
            # Correctly flip the frame
            frame = cv2.flip(frame, -1)
        
            
            
            # find the barcodes in the frame and decode each of the barcodes
            barcodes_list = pyzbar.decode(frame)

            # loop over the detected barcodes
            for barcode in barcodes_list:
                # the barcode data is a bytes object so we convert it to a string
                barcodeData = barcode.data.decode("utf-8")
                barcodeType = barcode.type

                # show the barcode detector border on screen
                (x, y, w, h) = barcode.rect
                cv2.rectangle(frame, (x, y), (x + w, y + h), (92, 92, 251), 2)

                # if the barcode text has not been seen before print it and update the set
                if barcodeData not in found:
                    
                    # print("[FOUND] Type: {}, Data: {}".format(barcodeType, barcodeData))
                    if barcodeData[0:8] == "engineer":
                        print("frame {}".format(frame_counter))
                        engineer_id = barcodeData
                        if frame_counter > 3:
                            continue_scanning = False
                        frame_counter += 1
                
            
            # Display the frame on UI
            self.change_pixmap_signal.emit(frame)
            # pause for 1 second before scanning again
            time.sleep(1)
        
        self.return_engineer_id_signal.emit(engineer_id)
        # When everything is done, release the capture
        vs.stop()
        
        self.stop()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.quit()