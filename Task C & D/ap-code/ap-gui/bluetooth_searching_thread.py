from PyQt5.QtCore import pyqtSignal, pyqtSlot, Qt, QThread
import time
import bluetooth
import subprocess

class BluetoothScanning(QThread):
    
    close_thread_signal = pyqtSignal(QThread)
    def __init__(self):
        super().__init__()
        self._run_flag = True
        
        # Symbolic initialization
        self.engineers_mac_list = []
        self.engineer_unlocked = False
        self.engineer_finished = False

    def run(self):   
        # initialize the video stream and allow the camera sensor to warm up
        
        self.engineers_mac_list.append("20:47:DA:B6:59:7B")
        subprocess.run("sudo rfkill unblock bluetooth", shell = True)
        time.sleep(1)
        
        
        # Start scaning for engineers
        while not self.engineer_unlocked:
            # Discover nearby devices
            nearbyDevices = bluetooth.discover_devices()

            if len(nearbyDevices) > 0:
                
                # Found all nearby devices
                for macAddress in nearbyDevices:            
                    print("found device {}".format(macAddress))
                    # Check if the MAC address is from an engineer        
                    if macAddress in self.engineers_mac_list:     
                        print("Unlocked")
                        self.engineer_unlocked = True
            else:
                print("Not found any device. Trying again")
            time.sleep(2)

        self.stop()

    def stop(self):
        """Sets run flag to False and waits for thread to finish"""
        self.quit()
        self.close_thread_signal.emit(self)