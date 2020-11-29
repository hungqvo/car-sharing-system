### REFERENCE: https://www.tutorialspoint.com/pyqt/pyqt_qstackedwidget.htm
### REFERENCE: https://gist.github.com/docPhil99/ca4da12c9d6f29b9cea137b617c7b8b1
### REFERENCE: https://www.tutorialspoint.com/python3/python_multithreading.htm
### REFERENCE: https://doc.qt.io/qt-5/qstackedwidget.html
### REFERENCE: https://wiki.python.org/moin/PyQt/Fading%20Between%20Widgets
### REFERENCE: https://stackoverflow.com/questions/49092390/displaying-getting-images-from-an-url-in-python
### REFERENCE: https://stackoverflow.com/questions/34697559/pil-image-to-qpixmap-conversion-issue
import sys 
import numpy as np
import os
import cv2
import _thread
import time
import requests
from numpy import random
from PIL import Image
from PIL.ImageQt import ImageQt
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import QWidget, QListWidget, QApplication, QHBoxLayout, QFormLayout, QLabel, QCheckBox, QLineEdit, QRadioButton, QStackedWidget
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
from facial_recognition.cv_encoder import FacialEncoder
from face_capture_thread import CvCapturing
from face_recognize_thread import CvRecognizing
from qr_scanner_thread import CvQrScanning
from login_checker import loginHandler
from booking_displayer import bookingHandler
from widget_fader import WidgetFader
from bluetooth_searching_thread import BluetoothScanning
from get_engineer_info import EngineerInfoChecker

class stackedUi(QWidget):
    def __init__(self):
        super(stackedUi, self).__init__()
		# Declare list of booked car dictionary
        self.booking_dictionaries = []

        # Declare constants representing each screen in UI
        self.HOME_SCREEN = 0
        self.FACIAL_REGISTER_SCREEN = 1
        self.FACIAL_LOGIN_SCREEN = 2
        self.QR_SCANNING_SCREEN = 3
        self.BOOKING_SCREEN = 4
        self.ENGINEER_SCREEN = 5

        # Declare how many widgets
        self.home_widget = QWidget()
        self.facial_register_widget = QWidget()
        self.facial_login_widget = QWidget()
        self.qr_scanning_widget = QWidget()
        self.booking_widget = QWidget()
        self.engineer_widget = QWidget()

        # Setting up each widget stack
        self.home_widget_ui()
        self.facial_register_ui()
        self.facial_login_ui()
        self.qr_scanner_ui()
        self.bookings_ui()
        self.engineer_details_ui()
            
        self.Stack = QStackedWidget (self)

        # this is where to add the Widgets
        # self.Stack.addWidget (self.qr_scanning_widget)
        self.Stack.addWidget (self.home_widget)
        self.Stack.addWidget (self.facial_register_widget)
        self.Stack.addWidget (self.facial_login_widget)
        self.Stack.addWidget (self.qr_scanning_widget)
        self.Stack.addWidget (self.booking_widget)
        self.Stack.addWidget (self.engineer_widget)
            
        hbox = QHBoxLayout(self)
        hbox.addWidget(self.Stack)

        # Setting up the main window
        self.setLayout(hbox)
        self.setGeometry(0, 0, 800, 480)
        self.setStyleSheet("background-color: rgb(255, 255, 255);")
        self.setWindowTitle('StackedWidget demo')
        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.show()
	
    # HOME SCREEN
    def home_widget_ui(self):    
        self.logo = QtWidgets.QLabel(self.home_widget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/exotic_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.carDisplay = QtWidgets.QLabel(self.home_widget)
        self.carDisplay.setGeometry(QtCore.QRect(360, 90, 381, 291))
        self.carDisplay.setText("")
        self.carDisplay.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/Sedans/Honda-Accord-Hybrid.png"))
        self.carDisplay.setScaledContents(True)
        self.carDisplay.setObjectName("carDisplay")
        self.login_button = QtWidgets.QPushButton(self.home_widget)
        self.login_button.setGeometry(QtCore.QRect(120, 250, 171, 32))
        self.login_button.setStyleSheet("QPushButton{\n"
        "border: none;\n"
        "background: #fb5c5c;\n"
        "color: white;\n"
        "}\n"
        "\n"
        "QPushButton:hover \n"
        "{\n"
        "  border: none; \n"
        "  background-color: white; \n"
        "  color: #fb5c5c;\n"
        "}\n"
        "")
        self.login_button.setCheckable(False)
        self.login_button.setObjectName("login_button")
        self.usernameField = QtWidgets.QLineEdit(self.home_widget)
        self.usernameField.setGeometry(QtCore.QRect(120, 140, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.usernameField.setFont(font)
        self.usernameField.setStyleSheet("QLineEdit{\n"
        "border: none;\n"
        "background: #eeeeee;\n"
        "border-radius: 2px;\n"
        "}")
        self.usernameField.setObjectName("usernameField")
        self.passwordField = QtWidgets.QLineEdit(self.home_widget)
        self.passwordField.setGeometry(QtCore.QRect(120, 190, 171, 31))
        font = QtGui.QFont()
        font.setPointSize(14)
        self.passwordField.setFont(font)
        self.passwordField.setStyleSheet("QLineEdit{\n"
        "border: none;\n"
        "background: #eeeeee;\n"
        "border-radius: 2px;\n"
        "}")
        self.passwordField.setEchoMode(QtWidgets.QLineEdit.Password)
        self.passwordField.setObjectName("passwordField")
        self.login_status = QtWidgets.QLabel(self.home_widget)
        self.login_status.setGeometry(QtCore.QRect(120, 295, 171, 31))
        font = QtGui.QFont()
        font.setBold(False)
        font.setItalic(True)
        font.setWeight(50)
        self.login_status.setFont(font)
        self.login_status.setStyleSheet("")
        self.login_status.setAlignment(QtCore.Qt.AlignCenter)
        self.login_status.setObjectName("login_status")
        self.login_status.setHidden(True)
        self.facial_description = QtWidgets.QLabel(self.home_widget)
        self.facial_description.setGeometry(QtCore.QRect(165, 365, 140, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.facial_description.setFont(font)
        self.facial_description.setAlignment(QtCore.Qt.AlignLeft)
        self.facial_description.setObjectName("facial_description")
        self.line = QtWidgets.QFrame(self.home_widget)
        self.line.setGeometry(QtCore.QRect(150, 330, 111, 20)) 
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.facial_button = QtWidgets.QPushButton(self.home_widget)
        self.facial_button.setGeometry(QtCore.QRect(120, 355, 40, 40))  
        self.facial_button.setStyleSheet("QPushButton{\n"
        "border: none\n"
        "}\n"
        "QPushButton:hover{\n"
        "border: 2px dashed #fb5c5c;\n"
        "}")
        self.facial_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/facial_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.facial_button.setIcon(icon)
        self.facial_button.setIconSize(QtCore.QSize(40, 40))
        self.facial_button.setObjectName("facial_button")

        self.secondary_button = QtWidgets.QPushButton(self.home_widget)
        self.secondary_button.setGeometry(QtCore.QRect(120, 395, 40, 40))
        self.secondary_button.setStyleSheet("QPushButton{\n"
        "border: none\n"
        "}\n"
        "QPushButton:hover{\n"
        "border: 2px dashed #fb5c5c;\n"
        "}")
        self.secondary_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/car_bookings.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.secondary_button.setIcon(icon)
        self.secondary_button.setIconSize(QtCore.QSize(40, 40))
        self.secondary_button.setObjectName("secondary_button")
        self.secondary_button.setHidden(True)

        self.secondary_description = QtWidgets.QLabel(self.home_widget)
        self.secondary_description.setGeometry(QtCore.QRect(165, 405, 140, 31))
        font = QtGui.QFont()
        font.setBold(True)
        font.setWeight(75)
        self.secondary_description.setFont(font)
        self.secondary_description.setAlignment(QtCore.Qt.AlignLeft)
        self.secondary_description.setObjectName("secondary_description")
        self.secondary_description.setHidden(True)

        _translate = QtCore.QCoreApplication.translate
        self.login_button.setText(_translate("HomeScreen", "LOG IN"))
        self.usernameField.setPlaceholderText(_translate("HomeScreen", "Username"))
        self.passwordField.setPlaceholderText(_translate("HomeScreen", "Password"))
        self.login_status.setText(_translate("HomeScreen", "Login Status"))
        self.facial_description.setText(_translate("HomeScreen", "Face Biometrics"))
        self.secondary_description.setText(_translate("HomeScreen", "Show Bookings"))
        
        self.login_button.clicked.connect(self.loginCheck)
        
    # FACIAL REGISTER SCREEN
    def facial_register_ui(self):
        self.logo = QtWidgets.QLabel(self.facial_register_widget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/exotic_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.instruction = QtWidgets.QLabel(self.facial_register_widget)
        self.instruction.setGeometry(QtCore.QRect(270, 400, 261, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.instruction.setFont(font)
        self.instruction.setAlignment(QtCore.Qt.AlignCenter)
        self.instruction.setObjectName("instruction")
        self.camera_feed = QtWidgets.QLabel(self.facial_register_widget)
        self.camera_feed.setGeometry(QtCore.QRect(250, 90, 300, 300))
        self.camera_feed.setText("")
        self.camera_feed.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/facial_scanner.png"))
        self.camera_feed.setScaledContents(True)
        self.camera_feed.setObjectName("camera_feed")

        self.logout_button = QtWidgets.QPushButton(self.facial_register_widget)
        self.logout_button.setGeometry(QtCore.QRect(200, 65, 81, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.logout_button.setFont(font)
        self.logout_button.setStyleSheet("QPushButton{\n"
        "border:none; outline:none\n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "color: #f85c5c;\n"
        "}")
        self.logout_button.setObjectName("logout_button")
        self.logout_button.setHidden(True)

        # Translate the UI (according to the framework)
        _translate = QtCore.QCoreApplication.translate
        self.instruction.setText(_translate("FacialRecognition", "Stand within the camera focal range"))
        self.logout_button.setText(_translate("FacialRecognition", "Log out"))

    # FACIAL LOGIN SCREEN
    def facial_login_ui(self):
        self.logo = QtWidgets.QLabel(self.facial_login_widget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/exotic_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.instruction = QtWidgets.QLabel(self.facial_login_widget)
        self.instruction.setGeometry(QtCore.QRect(270, 400, 261, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.instruction.setFont(font)
        self.instruction.setAlignment(QtCore.Qt.AlignCenter)
        self.instruction.setObjectName("instruction")
        self.camera_feed = QtWidgets.QLabel(self.facial_login_widget)
        self.camera_feed.setGeometry(QtCore.QRect(250, 90, 300, 300))
        self.camera_feed.setText("")
        self.camera_feed.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/facial_scanner.png"))
        self.camera_feed.setScaledContents(True)
        self.camera_feed.setObjectName("camera_feed")

        self.logout_button = QtWidgets.QPushButton(self.facial_login_widget)
        self.logout_button.setGeometry(QtCore.QRect(200, 65, 81, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.logout_button.setFont(font)
        self.logout_button.setStyleSheet("QPushButton{\n"
        "border:none; outline:none\n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "color: #f85c5c;\n"
        "}")
        self.logout_button.setObjectName("logout_button")
        self.logout_button.setHidden(True)

        # Translate the UI (according to the framework)
        _translate = QtCore.QCoreApplication.translate
        self.instruction.setText(_translate("FacialRecognition", "Stand within the camera focal range"))    
        self.logout_button.setText(_translate("FacialRecognition", "Log out"))

    # ENGINEER QR SCANNING SCREEN
    def qr_scanner_ui(self):
        self.logo = QtWidgets.QLabel(self.qr_scanning_widget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/exotic_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.instruction = QtWidgets.QLabel(self.qr_scanning_widget)
        self.instruction.setGeometry(QtCore.QRect(270, 400, 261, 20))
        font = QtGui.QFont()
        font.setBold(True)
        font.setItalic(False)
        font.setWeight(75)
        self.instruction.setFont(font)
        self.instruction.setAlignment(QtCore.Qt.AlignCenter)
        self.instruction.setObjectName("instruction")
        self.camera_feed = QtWidgets.QLabel(self.qr_scanning_widget)
        self.camera_feed.setGeometry(QtCore.QRect(250, 90, 300, 300))
        self.camera_feed.setText("")
        self.camera_feed.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/qr_scanner.png"))
        self.camera_feed.setScaledContents(True)
        self.camera_feed.setObjectName("camera_feed")

        # Translate the UI (according to the framework)
        _translate = QtCore.QCoreApplication.translate
        self.instruction.setText(_translate("QRScanning", "Put QR within camera range"))

       
        
    # BOOKINGS DISPLAY SCREEN
    def bookings_ui(self):
        self.logo = QtWidgets.QLabel(self.booking_widget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/exotic_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.carDisplay = QtWidgets.QLabel(self.booking_widget)
        self.carDisplay.setGeometry(QtCore.QRect(360, 90, 381, 291))
        self.carDisplay.setText("")
        self.carDisplay.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/Sedans/Honda-Accord-Hybrid.png"))
        self.carDisplay.setScaledContents(True)
        self.carDisplay.setObjectName("carDisplay")
        self.line = QtWidgets.QFrame(self.booking_widget)
        self.line.setGeometry(QtCore.QRect(120, 160, 61, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.car_name = QtWidgets.QLabel(self.booking_widget)
        self.car_name.setGeometry(QtCore.QRect(120, 130, 211, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.car_name.setFont(font)
        self.car_name.setObjectName("car_name")
        self.bid_label = QtWidgets.QLabel(self.booking_widget)
        self.bid_label.setGeometry(QtCore.QRect(120, 190, 110, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.bid_label.setFont(font)
        self.bid_label.setObjectName("bid_label")
        self.bid = QtWidgets.QLabel(self.booking_widget)
        self.bid.setGeometry(QtCore.QRect(220, 190, 81, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.bid.setFont(font)
        self.bid.setObjectName("bid")
        self.date_label = QtWidgets.QLabel(self.booking_widget)
        self.date_label.setGeometry(QtCore.QRect(120, 220, 61, 16))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.date_label.setFont(font)
        self.date_label.setObjectName("date_label")
        self.from_time = QtWidgets.QLabel(self.booking_widget)
        self.from_time.setGeometry(QtCore.QRect(220, 250, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.from_time.setFont(font)
        self.from_time.setObjectName("from_time")
        self.from_label = QtWidgets.QLabel(self.booking_widget)
        self.from_label.setGeometry(QtCore.QRect(120, 250, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.from_label.setFont(font)
        self.from_label.setObjectName("from_label")
        self.date = QtWidgets.QLabel(self.booking_widget)
        self.date.setGeometry(QtCore.QRect(220, 220, 91, 16))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.date.setFont(font)
        self.date.setObjectName("date")
        self.line_2 = QtWidgets.QFrame(self.booking_widget)
        self.line_2.setGeometry(QtCore.QRect(120, 310, 61, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        self.locked_button = QtWidgets.QPushButton(self.booking_widget)
        self.locked_button.setGeometry(QtCore.QRect(120, 330, 31, 40))
        self.locked_button.setStyleSheet("QPushButton{\n"
        "border:none;\n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "\n"
        "border: 2px dashed #fb5c5c;\n"
        "}")
        self.locked_button.setText("")
        icon = QtGui.QIcon()
        icon.addPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/locked.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.locked_button.setIcon(icon)
        self.locked_button.setIconSize(QtCore.QSize(40, 40))
        self.locked_button.setObjectName("locked_button")
        self.lock_status = QtWidgets.QLabel(self.booking_widget)
        self.lock_status.setGeometry(QtCore.QRect(160, 350, 181, 16))
        self.lock_status.setObjectName("lock_status")
        self.unlocked_button = QtWidgets.QPushButton(self.booking_widget)
        self.unlocked_button.setGeometry(QtCore.QRect(120, 330, 31, 40))
        self.unlocked_button.setStyleSheet("QPushButton{\n"
        "border:none;\n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "\n"
        "border: 2px dashed #fb5c5c;\n"
        "}")
        self.unlocked_button.setText("")
        icon1 = QtGui.QIcon()
        icon1.addPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/unlocked.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.unlocked_button.setIcon(icon1)
        self.unlocked_button.setIconSize(QtCore.QSize(40, 40))
        self.unlocked_button.setObjectName("unlocked_button")
        self.unlocked_button.setHidden(True)
        self.parking = QtWidgets.QLabel(self.booking_widget)
        self.parking.setGeometry(QtCore.QRect(220, 380, 141, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.parking.setFont(font)
        self.parking.setObjectName("parking")
        self.parking.setHidden(True)
        self.parking_label = QtWidgets.QLabel(self.booking_widget)
        self.parking_label.setGeometry(QtCore.QRect(120, 380, 91, 21))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.parking_label.setFont(font)
        self.parking_label.setObjectName("parking_label")
        self.parking_label.setHidden(True)
        self.duration_label = QtWidgets.QLabel(self.booking_widget)
        self.duration_label.setGeometry(QtCore.QRect(120, 280, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.duration_label.setFont(font)
        self.duration_label.setObjectName("duration_label")
        self.duration = QtWidgets.QLabel(self.booking_widget)
        self.duration.setGeometry(QtCore.QRect(220, 280, 71, 16))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.duration.setFont(font)
        self.duration.setObjectName("duration")
        self.next_button = QtWidgets.QPushButton(self.booking_widget)
        self.next_button.setGeometry(QtCore.QRect(735, 210, 41, 31))
        self.next_button.setStyleSheet("QPushButton{\n"
        "border:none;\n"
        "}\n"
        "QPushButton:hover{\n"
        "\n"
        "border: 2px dashed #fb5c5c;\n"
        "}"
        )
        self.next_button.setText("")
        icon2 = QtGui.QIcon()
        icon2.addPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/next_button.png"), QtGui.QIcon.Normal, QtGui.QIcon.Off)
        self.next_button.setIcon(icon2)
        self.next_button.setIconSize(QtCore.QSize(40, 40))
        self.next_button.setObjectName("next_button")
        self.booking_counter = QtWidgets.QLabel(self.booking_widget)
        self.booking_counter.setGeometry(QtCore.QRect(735, 190, 41, 16))
        font = QtGui.QFont()
        font.setPointSize(14)
        font.setBold(True)
        font.setWeight(75)
        self.booking_counter.setFont(font)
        self.booking_counter.setAlignment(QtCore.Qt.AlignCenter)
        self.booking_counter.setObjectName("booking_counter")
        
        
        self.logout_button = QtWidgets.QPushButton(self.booking_widget)
        self.logout_button.setGeometry(QtCore.QRect(200, 60, 81, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.logout_button.setFont(font)
        self.logout_button.setStyleSheet("QPushButton{\n"
        "border:none; outline:none\n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "color: #f85c5c;\n"
        "}")
        self.logout_button.setObjectName("logout_button")

        
        _translate = QtCore.QCoreApplication.translate
        
        self.car_name.setText(_translate("ShowBookingScreen", "HONDA  ACCORD"))
        self.bid_label.setText(_translate("ShowBookingScreen", "Booking ID:"))
        self.bid.setText(_translate("ShowBookingScreen", "2"))
        self.date_label.setText(_translate("ShowBookingScreen", "Date:"))
        self.from_time.setText(_translate("ShowBookingScreen", "09:00"))
        self.from_label.setText(_translate("ShowBookingScreen", "From:"))
        self.date.setText(_translate("ShowBookingScreen", "09-02-2020"))
        self.lock_status.setText(_translate("ShowBookingScreen", "Click to unlock this car"))
        self.parking.setText(_translate("ShowBookingScreen", "Parking | Slot D2.3"))
        self.parking_label.setText(_translate("ShowBookingScreen", "Location:"))
        self.duration_label.setText(_translate("ShowBookingScreen", "Duration:"))
        self.duration.setText(_translate("ShowBookingScreen", "24 hours"))
        self.booking_counter.setText(_translate("ShowBookingScreen", "2"))
        self.logout_button.setText(_translate("ShowBookingScreen", "Log out"))

    # Engineer Details UI
    def engineer_details_ui(self):
        self.logo = QtWidgets.QLabel(self.engineer_widget)
        self.logo.setGeometry(QtCore.QRect(100, 20, 121, 111))
        self.logo.setText("")
        self.logo.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/exotic_logo.png"))
        self.logo.setScaledContents(True)
        self.logo.setObjectName("logo")
        self.carDisplay = QtWidgets.QLabel(self.engineer_widget)
        self.carDisplay.setGeometry(QtCore.QRect(360, 90, 381, 291))
        self.carDisplay.setText("")
        self.carDisplay.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/Sedans/Honda-Accord-Hybrid.png"))
        self.carDisplay.setScaledContents(True)
        self.carDisplay.setObjectName("carDisplay")
        self.line = QtWidgets.QFrame(self.engineer_widget)
        self.line.setGeometry(QtCore.QRect(120, 160, 61, 20))
        self.line.setFrameShape(QtWidgets.QFrame.HLine)
        self.line.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line.setObjectName("line")
        self.welcome = QtWidgets.QLabel(self.engineer_widget)
        self.welcome.setGeometry(QtCore.QRect(120, 130, 220, 31))
        font = QtGui.QFont()
        font.setPointSize(20)
        font.setBold(True)
        font.setWeight(75)
        self.welcome.setFont(font)
        self.welcome.setObjectName("welcome")
        self.firstname_label = QtWidgets.QLabel(self.engineer_widget)
        self.firstname_label.setGeometry(QtCore.QRect(120, 190, 115, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.firstname_label.setFont(font)
        self.firstname_label.setObjectName("firstname_label")
        self.firstname = QtWidgets.QLabel(self.engineer_widget)
        self.firstname.setGeometry(QtCore.QRect(220, 190, 81, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.firstname.setFont(font)
        self.firstname.setObjectName("firstname")
        self.lastname_label = QtWidgets.QLabel(self.engineer_widget)
        self.lastname_label.setGeometry(QtCore.QRect(120, 220, 81, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.lastname_label.setFont(font)
        self.lastname_label.setObjectName("lastname_label")
        self.username = QtWidgets.QLabel(self.engineer_widget)
        self.username.setGeometry(QtCore.QRect(220, 250, 84, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.username.setFont(font)
        self.username.setObjectName("username")
        self.username_label = QtWidgets.QLabel(self.engineer_widget)
        self.username_label.setGeometry(QtCore.QRect(120, 250, 81, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.username_label.setFont(font)
        self.username_label.setObjectName("username_label")
        self.lastname = QtWidgets.QLabel(self.engineer_widget)
        self.lastname.setGeometry(QtCore.QRect(220, 220, 81, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.lastname.setFont(font)
        self.lastname.setObjectName("lastname")
        self.line_2 = QtWidgets.QFrame(self.engineer_widget)
        self.line_2.setGeometry(QtCore.QRect(120, 310, 61, 20))
        self.line_2.setFrameShape(QtWidgets.QFrame.HLine)
        self.line_2.setFrameShadow(QtWidgets.QFrame.Sunken)
        self.line_2.setObjectName("line_2")
        
        
        self.usertype_label = QtWidgets.QLabel(self.engineer_widget)
        self.usertype_label.setGeometry(QtCore.QRect(120, 280, 71, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        font.setBold(True)
        font.setWeight(75)
        self.usertype_label.setFont(font)
        self.usertype_label.setObjectName("usertype_label")
        self.usertype = QtWidgets.QLabel(self.engineer_widget)
        self.usertype.setGeometry(QtCore.QRect(220, 280, 71, 23))
        font = QtGui.QFont()
        font.setPointSize(13)
        self.usertype.setFont(font)
        self.usertype.setObjectName("usertype")
        
        
        self.logout_button = QtWidgets.QPushButton(self.engineer_widget)
        self.logout_button.setGeometry(QtCore.QRect(200, 60, 81, 32))
        font = QtGui.QFont()
        font.setBold(True)
        font.setUnderline(True)
        font.setWeight(75)
        self.logout_button.setFont(font)
        self.logout_button.setStyleSheet("QPushButton{\n"
        "border:none; outline:none\n"
        "}\n"
        "\n"
        "QPushButton:hover{\n"
        "color: #f85c5c;\n"
        "}")
        self.logout_button.setObjectName("logout_button")

        
        _translate = QtCore.QCoreApplication.translate
        
        self.welcome.setText(_translate("EngineerScreen", "ENGINEER DETAILS"))
        self.firstname_label.setText(_translate("EngineerScreen", "Firstname:"))
        self.firstname.setText(_translate("EngineerScreen", "2"))
        self.lastname_label.setText(_translate("EngineerScreen", "Lastname:"))
        self.username.setText(_translate("EngineerScreen", "09:00"))
        self.username_label.setText(_translate("EngineerScreen", "Username:"))
        self.lastname.setText(_translate("EngineerScreen", "09-02-2020"))
        self.usertype_label.setText(_translate("EngineerScreen", "Type:"))
        self.logout_button.setText(_translate("EngineerScreen", "Log out"))

    ### Facial Register threads and signals
    def start_face_capture_thread(self, user_dict):    
        self.thread = CvCapturing(user_dict)
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.close_thread_signal.connect(self.finished_face_capturing)
        self.thread.show_booking_signal.connect(self.show_booking_for_user)
        # start the thread
        self.thread.start()

    ### Facial Register pyqtSlot signals
    @pyqtSlot()
    def finished_face_capturing(self):
        # start encoding without blocking the UI thread
        _thread.start_new_thread(FacialEncoder.start_encoding, ("Thread-2",))   

    @pyqtSlot(str)
    def show_booking_for_user(self, userId):
        # Update UI
        self.facial_register_widget.findChild(QtWidgets.QLabel, "camera_feed").\
            setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/facial_verified.png"))
        
        self.facial_register_widget.findChild(QtWidgets.QLabel, "instruction").\
            setText("Success! Showing your booking...")

        self.show_bookings(userId)


    ### Facial Login threads and signals
    def start_face_login_thread(self):    
        self.thread = CvRecognizing()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.update_instruction_signal.connect(self.show_customer_name)
        self.thread.close_thread_signal.connect(self.finished_face_login)
        # start the thread
        self.thread.start()

    @pyqtSlot(str)
    def show_customer_name(self, customer_name):
        if customer_name == "Unknown":
            instruction = self.facial_login_widget.findChild(QtWidgets.QLabel, "instruction")
            instruction.setText("Cannot verify faceID")
            
            image = self.facial_login_widget.findChild(QtWidgets.QLabel, "camera_feed")
            image.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/facial_unverified.png"))
        
        else:    
            instruction = self.facial_login_widget.findChild(QtWidgets.QLabel, "instruction")
            instruction.setText("WELCOME, {}!".format(customer_name[0:8]))
            
            image = self.facial_login_widget.findChild(QtWidgets.QLabel, "camera_feed")
            image.setPixmap(QtGui.QPixmap("ap-code/ap-gui/image_resources/facial_verified.png"))
            self.show_bookings(customer_name)
        
    ### Facial Register pyqtSlot signals
    @pyqtSlot()
    def finished_face_login(self): 
        # Reset UI
        print("DONE")
    
    ### Bluetooth detection thread
    def start_searching_bluetooth(self):
        self.thread = BluetoothScanning()
        # connect its signal to the update_image slot
        self.thread.close_thread_signal.connect(self.finished_bluetooth_scanning)
        # start the thread
        self.thread.start()
    
    ### QR Scanner pyqtSlot signals
    @pyqtSlot()
    def finished_bluetooth_scanning(self):
        # Transition screen
        data_tuple = (self.QR_SCANNING_SCREEN, "")
        self.display(data_tuple)

    ### QR Scanner threads and signals
    def start_qr_thread(self):    
        self.thread = CvQrScanning()
        # connect its signal to the update_image slot
        self.thread.change_pixmap_signal.connect(self.update_image)
        self.thread.return_engineer_id_signal.connect(self.finished_qr_scanning)
        # start the thread
        self.thread.start()

    ### QR Scanner pyqtSlot signals
    @pyqtSlot(str)
    def finished_qr_scanning(self, engineer_id):

        # Getting info
        engineer_details = EngineerInfoChecker.get_engineer_by_id(engineer_id)

        firstname = engineer_details["firstName"]
        lastname = engineer_details["lastName"]
        username = engineer_details["userName"]
        userType = engineer_details["userType"]
        
        # Setting up UI
        self.engineer_widget.findChild(QtWidgets.QLabel, "firstname").setText(firstname)
        self.engineer_widget.findChild(QtWidgets.QLabel, "lastname").setText(lastname)
        self.engineer_widget.findChild(QtWidgets.QLabel, "username").setText(username)
        self.engineer_widget.findChild(QtWidgets.QLabel, "usertype").setText(userType)
        self.engineer_widget.findChild(QtWidgets.QPushButton, "logout_button").clicked.connect(\
            self.reset_all)
        # Transition screen into profile 
        data_tuple = (self.ENGINEER_SCREEN, "")
        self.display(data_tuple)
   
    ### Convert CV images into QT image format
    def convert_cv_qt(self, cv_img):
        """Convert from an opencv image to QPixmap"""
        rgb_image = cv2.cvtColor(cv_img, cv2.COLOR_BGR2RGB)
        h, w, ch = rgb_image.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = QtGui.QImage(rgb_image.data, w, h, bytes_per_line, QtGui.QImage.Format_RGB888)
        return QPixmap.fromImage(convert_to_Qt_format)    

    @pyqtSlot(np.ndarray)
    def update_image(self, cv_img):
        """Updates the image_label with a new opencv image"""
        qt_img = self.convert_cv_qt(cv_img)
        if self.Stack.currentIndex() == self.FACIAL_REGISTER_SCREEN:
            self.facial_register_widget.findChild(QtWidgets.QLabel, "camera_feed").setPixmap(qt_img)
        elif self.Stack.currentIndex() == self.FACIAL_LOGIN_SCREEN:
            self.facial_login_widget.findChild(QtWidgets.QLabel, "camera_feed").setPixmap(qt_img)
        elif self.Stack.currentIndex() == self.QR_SCANNING_SCREEN:
            self.qr_scanning_widget.findChild(QtWidgets.QLabel, "camera_feed").setPixmap(qt_img)

	### Changing screen using display or threaded_display
    def display(self,data_tuple):
        # Index of screen to transition to is always at the start of tuple
        stack_index = data_tuple[0]
        # Implement fading effects between screens
        self.fader_widget = WidgetFader(self.Stack.currentWidget(), self.Stack.widget(stack_index))
        
        # Set screen index to Stack
        self.Stack.setCurrentIndex(stack_index)
        # if it is the facial recognition screen
        if stack_index == self.FACIAL_REGISTER_SCREEN:
            user_dict = data_tuple[1]
            self.start_face_capture_thread(user_dict)
        # if it is the facial login screen
        elif stack_index == self.FACIAL_LOGIN_SCREEN:
            self.start_face_login_thread()
        # if it is the qr scanning screen
        elif stack_index == self.QR_SCANNING_SCREEN:
            self.start_qr_thread()        


    # Change screen while multi-threading
    def threaded_display(self,thread_name,data_tuple):
        stack_index = data_tuple[0]

        # Transition into new screen
        self.Stack.setCurrentIndex(stack_index)

    def loginCheck(self):
        username = self.usernameField.text()
        password = self.passwordField.text()

        # Check if the fields are filled        
        if username == "" or password == "":
            self.login_status.setText("Fill both fields!")
            self.login_status.setHidden(False)

        else:
            
            user_dict = loginHandler.credential_check(username, password)
            if user_dict != None:
                # self.login_button.setText("Signed in")
                userId = user_dict["userId"]
                userName = user_dict["userName"]
                self.login_button.setDisabled(True)
                # Check facial recognition registered?
                folder = "ap-code/ap-gui/facial_recognition/dataset/{}".format(userName)

                secondary_button = self.home_widget.findChild(QtWidgets.QPushButton, "secondary_button")
                secondary_description = self.home_widget.findChild(QtWidgets.QLabel, "secondary_description")
                secondary_button.setHidden(False)
                secondary_description.setHidden(False)

                secondary_button.clicked.connect(lambda: self.show_bookings(userId))

                # User has already registered for facial recognition
                if os.path.exists(folder):
                    
                    self.login_status.setText("Signed in")
                    self.login_status.setHidden(False)
                    self.home_widget.findChild(QtWidgets.QLabel, "facial_description").setHidden(True)
                    self.home_widget.findChild(QtWidgets.QPushButton, "facial_button").setHidden(True)
                    self.secondary_button.setGeometry(QtCore.QRect(120, 355, 40, 40))
                    self.secondary_description.setGeometry(QtCore.QRect(165, 365, 140, 31))

                # Prompt user to register if not
                else:
                    self.register_facial_recognition(user_dict)
                
                                              
            else:
                self.login_status.setText("Invalid sign in")
                self.login_status.setHidden(False)

    def register_facial_recognition(self, user_dict):
        login_status = self.home_widget.findChild(QtWidgets.QLabel, "login_status")
        facial_description = self.home_widget.findChild(QtWidgets.QLabel, "facial_description")
        
        login_status.setText("Login faster with FaceID?")
        login_status.setHidden(False)
        facial_description.setText("Get your FaceID")
        self.home_widget.findChild(QtWidgets.QLabel, "facial_description").setHidden(False)
        self.home_widget.findChild(QtWidgets.QPushButton, "facial_button").setHidden(False)
        self.secondary_description.setGeometry(QtCore.QRect(165, 405, 140, 31))
        self.secondary_button.setGeometry(QtCore.QRect(120, 395, 40, 40))
        facial_button = self.home_widget.findChild(QtWidgets.QPushButton, "facial_button")
        
        # Use tuple to pass multiple values into function
        my_data_tuple = (self.FACIAL_REGISTER_SCREEN, user_dict)
        # Disconnect the previous clicked signal
        facial_button.clicked.disconnect()
        facial_button.clicked.connect(lambda: self.display(my_data_tuple))
        

    def show_bookings(self, user_id):
        # Check booked car
        # cars_Id = bookingHandler.show_booking(user_id)
        bookings = bookingHandler.show_booking(user_id)
        if len(bookings) > 0: 
            # print("Booked some cars")
            for booking in bookings:
                booking_id = booking["booking_id"]
                car_id = booking["booking_car_id"]
                booking_date = booking["booking_date"]
                booking_duration = booking["booking_duration"]
                booking_from_time = booking["booking_from"]

                # Find details about car
                car_details = bookingHandler.get_user_booked_car(car_id)
                car_brand = car_details["car_brand"]
                car_name = car_details["car_name"]
                car_image_url = car_details["car_image"]

                response = requests.get(car_image_url, stream=True)
                img = Image.open(response.raw)
                img_qt = ImageQt(img)

                # Randomize location
                
                random.seed(int(car_id))
                slot = random.randint(1,7)
                space = random.randint(1,9)
                location = "Parking | Slot D" + str(slot) + "." + str(space)

                car_name = car_brand + " " + car_name
            
                booking_dictionary = {
                    "booking_id": booking_id,
                    "booking_date": booking_date,
                    "booking_from_time": booking_from_time,
                    "booking_duration": booking_duration,
                    "booking_car_name": car_name,
                    "booking_car_image": img_qt,
                    "booking_car_location": location,
                    "booking_unlock_status": False,
                }

                self.booking_dictionaries.append(booking_dictionary)

            self.booking_displayer(0, True)             
            
        else:
            # If user come from Facial Recognition Screen:
            if self.Stack.currentIndex() == self.FACIAL_REGISTER_SCREEN:
                self.facial_register_widget.findChild(QtWidgets.QLabel, "instruction").setText("You have not booked any car")
                logout_button = self.facial_register_widget.findChild(QtWidgets.QPushButton, "logout_button")
                logout_button.setHidden(False)
                logout_button.clicked.connect(self.reset_all)

            # If user come from Facial Login Screen:
            elif self.Stack.currentIndex() == self.FACIAL_LOGIN_SCREEN:
                self.facial_login_widget.findChild(QtWidgets.QLabel, "instruction").setText("You have not booked any car")
                logout_button = self.facial_login_widget.findChild(QtWidgets.QPushButton, "logout_button")
                logout_button.setHidden(False)
                logout_button.clicked.connect(self.reset_all)
            
            # If user come from Home Screen:
            elif self.Stack.currentIndex() == self.HOME_SCREEN:
                self.home_widget.findChild(QtWidgets.QLabel, "login_status").setText("No car is booked")
                self.home_widget.findChild(QtWidgets.QLineEdit, "usernameField").setText("")
                self.home_widget.findChild(QtWidgets.QLineEdit, "passwordField").setText("")
                self.home_widget.findChild(QtWidgets.QPushButton, "login_button").setDisabled(False)
                self.home_widget.findChild(QtWidgets.QPushButton, "secondary_button").setHidden(True)
                self.home_widget.findChild(QtWidgets.QLabel, "secondary_description").setHidden(True)
                self.home_widget.findChild(QtWidgets.QPushButton, "secondary_button")
                self.home_widget.findChild(QtWidgets.QLabel, "facial_description").setText("Facial Biometrics")
                self.home_widget.findChild(QtWidgets.QLabel, "facial_description").setHidden(False)
                facial_recognizer_button = self.home_widget.findChild(QtWidgets.QPushButton, "facial_button")
                facial_recognizer_button.setHidden(False)
                data_tuple = (self.FACIAL_LOGIN_SCREEN,"")
                facial_recognizer_button.clicked.connect(lambda: self.display(data_tuple))

    # Function to handle display multiple booked cars
    def booking_displayer(self, booking_index, first_called):
        number_of_bookings = len(self.booking_dictionaries)
        # Reach the last car index
        if booking_index == number_of_bookings:
            booking_index = 0
        next_index = booking_index + 1
        
        # Setup UI
        logout_button = self.booking_widget.findChild(QtWidgets.QPushButton, "logout_button")
        logout_button.clicked.connect(self.reset_all)
        booking_counter_label = self.booking_widget.findChild(QtWidgets.QLabel, "booking_counter")
        next_button = self.booking_widget.findChild(QtWidgets.QPushButton, "next_button")
        car_name_label = self.booking_widget.findChild(QtWidgets.QLabel, "car_name")
        car_image_label = self.booking_widget.findChild(QtWidgets.QLabel, "carDisplay")
        booking_id_label = self.booking_widget.findChild(QtWidgets.QLabel, "bid")
        date_label = self.booking_widget.findChild(QtWidgets.QLabel, "date")
        from_label = self.booking_widget.findChild(QtWidgets.QLabel, "from_time")
        duration_label = self.booking_widget.findChild(QtWidgets.QLabel, "duration")
        unlocked_button = self.booking_widget.findChild(QtWidgets.QPushButton, "unlocked_button")
        locked_button = self.booking_widget.findChild(QtWidgets.QPushButton, "locked_button")
        locked_label = self.booking_widget.findChild(QtWidgets.QLabel, "lock_status")
        location_label = self.booking_widget.findChild(QtWidgets.QLabel, "parking_label")
        location = self.booking_widget.findChild(QtWidgets.QLabel, "parking")
        
        # User booked 1 car
        if number_of_bookings == 1:
            booking_counter_label.setHidden(True)
            next_button.setHidden(True)
            
        else:
            booking_counter_label.setText(str(number_of_bookings))

        # Update display   
        unlock_status = self.booking_dictionaries[booking_index]["booking_unlock_status"]

        # Unlocked
        if unlock_status:
            locked_button.setHidden(True)
            unlocked_button.setHidden(False)
            locked_label.setText("Car has been unlocked")
            location.setHidden(False)
            location_label.setHidden(False)
        # Locked
        else:
            locked_button.setHidden(False)
            unlocked_button.setHidden(True)
            locked_label.setText("Click to unlock this car")
            location.setHidden(True)
            location_label.setHidden(True)     
        
        # Setup UI
        car_name_label.setText(self.booking_dictionaries[booking_index]["booking_car_name"])
        booking_id_label.setText(self.booking_dictionaries[booking_index]["booking_id"])
        date_label.setText(self.booking_dictionaries[booking_index]["booking_date"])
        from_label.setText(self.booking_dictionaries[booking_index]["booking_from_time"])
        duration_label.setText(str(self.booking_dictionaries[booking_index]["booking_duration"])+" hours")
        car_image_label.setPixmap(\
        QtGui.QPixmap.fromImage(self.booking_dictionaries[booking_index]["booking_car_image"])) 
        location.setText(self.booking_dictionaries[booking_index]["booking_car_location"])
        
        # Manually set clicked signal depending on they are first called or not
        if first_called:
            next_button.clicked.connect(lambda: self.booking_displayer(next_index, False))
            locked_button.clicked.connect(lambda: self.unlock_car(booking_index))
            unlocked_button.clicked.connect(lambda: self.lock_car(booking_index))
            data_tuple = (self.BOOKING_SCREEN,"")
            self.display(data_tuple)
        
        # Refresh behavior to ensure smooth execution
        else:
            next_button.clicked.disconnect()
            locked_button.clicked.disconnect()
            unlocked_button.clicked.disconnect()
            
            next_button.clicked.connect(lambda: self.booking_displayer(next_index, False))
            locked_button.clicked.connect(lambda: self.unlock_car(booking_index))
            unlocked_button.clicked.connect(lambda: self.lock_car(booking_index))

    def unlock_car(self, car_index):
        self.booking_dictionaries[car_index]["booking_unlock_status"] = True
        self.booking_displayer(car_index, False)
    
    def lock_car(self, car_index):
        self.booking_dictionaries[car_index]["booking_unlock_status"] = False
        self.booking_displayer(car_index, False)

    def reset_all(self):
        # Reseting
        self.booking_dictionaries = []
        self.home_widget.findChild(QtWidgets.QLabel, "login_status").setHidden(True)
        self.home_widget.findChild(QtWidgets.QLineEdit, "usernameField").setText("")
        self.home_widget.findChild(QtWidgets.QLineEdit, "passwordField").setText("")
        self.home_widget.findChild(QtWidgets.QPushButton, "login_button").setDisabled(False)
        self.home_widget.findChild(QtWidgets.QPushButton, "secondary_button").setHidden(True)
        self.home_widget.findChild(QtWidgets.QLabel, "secondary_description").setHidden(True)
        self.home_widget.findChild(QtWidgets.QPushButton, "secondary_button")
        self.home_widget.findChild(QtWidgets.QLabel, "facial_description").setText("Facial Biometrics")
        facial_recognizer_button = self.home_widget.findChild(QtWidgets.QPushButton, "facial_button")
        data_tuple = (self.FACIAL_LOGIN_SCREEN,"")
        facial_recognizer_button.clicked.connect(lambda: self.display(data_tuple))
        self.start_searching_bluetooth()

        # Switch the main screen
        data_tuple = (self.HOME_SCREEN, "")
        self.display(data_tuple)
        
        
def main():
    app = QApplication(sys.argv)
    ui = stackedUi()

    # Assign methods to button.clicked signal to change screen
    facial_recognizer_button = ui.home_widget.findChild(QtWidgets.QPushButton, "facial_button")
    data_tuple = (ui.FACIAL_LOGIN_SCREEN,"")
    facial_recognizer_button.clicked.connect(lambda: ui.display(data_tuple))
    
    # Start scanning for engineers
    ui.start_searching_bluetooth()

    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
