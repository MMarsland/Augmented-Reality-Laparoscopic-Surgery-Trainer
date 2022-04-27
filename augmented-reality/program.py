'''This file contains the main code for the Laparoscopic Surgery Trainer Program.

To run the project on the jetson nano or on a computer this file should be run
with "py program.py". The main code here will create all the required objects
and display the program on the configured attached monitor.

Some configuration is required in this file in the __main__ block depending
on the circumstance and the device this program is running on, as well as the
size of the attached monitor.

@Author: Michael Marsland
@Date: April 2022
'''

# OpenCV
import cv2
# Numpy
import numpy as np
#  Serial
import serial
# Threading
import threading
# Other Improts
from datetime import datetime, timedelta
import random
import time
import threading
import tkinter as tk
import math

# Import Local Classes
# Import Analyzer from Rahme
from analyzer import Analyzer
# Import Arduino classes
from arduino import Arduino, ArduinoSim
# Import Motion Tracking
from motionTracker import MotionTracker
# Import Augmented Reality
from augmentedReality import AR


class App():
    '''The main application for the program.

    This class more or less hosts all the other classes for the program to run and is
    currently the central parent for the program. Classes can interact with eachother
    through the app which is passes around as a parent. Restructuring of the class system
    could improve the code flow. The app is currently run through the connected color
    calibration window on a separate thread to comply with tkinter.
    '''
    def __init__(self, cameraID, motionTracker, colorCalibrationWindow, height, width):
        self.motionTracker = motionTracker

        self.colorCalibration = colorCalibrationWindow
        self.colorCalibration.connectApp(app=self)

        self.AR = AR(self, cameraID, height, width)
        self.keyboardInput = ""
        self.analyzer = Analyzer()

    def run(self):
        self.AR.run()


class ColorCalibrationWindow(tk.Tk):
    '''Contains the code for opening a Color Calibration Window

    The color calibraton window is a very quickly written helper for adjusting the HSV
    ranges that the program uses to detect and mask specific colors. It was useful when
    often demoing the program in various lighting environments. In the future a better
    solution for color detection that is more robust would be preferred.
    '''
    def __init__(self):
        super().__init__()
        self.title("Color Calibration")
        self.geometry('250x200+10+10')

        self.name = tk.Label(self, text="Color Calibration")
        self.name.config(font=("Courier", 12))
        self.name.grid(row=0,column=0)

        self.currentColorName = tk.StringVar(self)
        self.currentColorName.set("black") # default value

        self.colorNames = ["black", "red1", "red2", "yellow", "green", "brown", "white", "blue"]
        self.colorNameDropdown = tk.OptionMenu(self, self.currentColorName, *self.colorNames, command=self.updateLimitsText)
        self.colorNameDropdown.grid(row=1,column=0)

        self.newLimit = tk.Label(self, text="Waiting...")
        self.newLimit.grid(row=2,column=0)

        self.updateOnClick = tk.IntVar()
        self.checkBox = tk.Checkbutton(self, text='Update Limit?', variable=self.updateOnClick, onvalue=1, offvalue=0)
        self.checkBox.grid(row=3,column=0)

        self.calibrated_color_limits = {'black':  [[179, 255, 105], [0, 0, 0]],
                                        'red1':   [[9, 255, 255],   [0, 50, 70]],
                                        'red2':   [[180, 255, 255], [159, 50, 70]],
                                        'yellow': [[35, 255, 255],  [25, 50, 70]],
                                        'green':  [[80, 255, 255],  [45, 50, 70]],
                                        'brown':  [[20, 255, 200],  [10, 100, 20]],
                                        'white':  [[180, 255, 255], [0, 0, 231]],
                                        'blue':   [[128, 255, 255], [95, 50, 70]]}
        self.updateFromFile = False
        if self.updateFromFile:                     
            with open("color_calibration.txt") as f:
                for line in f:
                    (key, upperLimitText, lowerLimitText) = line.split("-")
                    self.calibrated_color_limits[key] = [[int(numeric_string) for numeric_string in upperLimitText.split(",")], [int(numeric_string) for numeric_string in lowerLimitText.split(",")]]

        self.limits = tk.Label(self, text=f"{self.calibrated_color_limits[self.currentColorName.get()]}")
        self.limits.grid(row=4,column=0)

        self.inputtxt = tk.Text(self,
                            height = 1,
                            width = 30)
        self.inputtxt.grid(row=5,column=0)

        self.setLimitsButton = tk.Button(self, text="Update Limits", command=self.updateLimits)
        self.setLimitsButton.grid(row=6,column=0)
        
    def run(self):
        self.after(1000, self.startAppThread)    
        self.mainloop()

    def startAppThread(self):
        def appThread():
            print("Running App Thread")
            self.app.run()

        x = threading.Thread(target=appThread)
        x.start()

    def connectApp(self, app):
        self.app = app

    def close(self):
        print("Closing Color Calibration Window")
        self.destroy()

    def updateLimits(self):
        newLimits = self.inputtxt.get("1.0", "end-1c")
        print(newLimits)

        # Form: [[100, 255, 255], [90, 50, 70]]
        newLimitsArr = newLimits[2:-2].split("], [")
        upperLimitText = newLimitsArr[0]
        lowerLimitText = newLimitsArr[1]

        upperLimitArr = upperLimitText.split(",")
        upperLimit = [int(upperLimitArr[0]), int(upperLimitArr[1]), int(upperLimitArr[2])]

        lowerLimitArr = lowerLimitText.split(",")
        lowerLimit = [int(lowerLimitArr[0]), int(lowerLimitArr[1]), int(lowerLimitArr[2])]


        # Upper Limit
        self.calibrated_color_limits[self.currentColorName.get()][0] = upperLimit
        # Lower Limit
        self.calibrated_color_limits[self.currentColorName.get()][1] = lowerLimit

        # Update File
        self.writeCalibrationToFile()

        self.updateLimitsText()

    def updateLimitsText(self, event=None):
        self.limits.config(text=f"{self.calibrated_color_limits[self.currentColorName.get()]}")

    def addColorToLimit(self, item):
        self.newLimit.config(text=f"{item}")
        print(item)

        if self.updateOnClick.get() == 1:
            # Add to limit, expand range in dict
            currentLimits = self.calibrated_color_limits[self.currentColorName.get()]
            # If item is greater than upper or less than lower
            if item[0] > currentLimits[0][0] or item[1] > currentLimits[0][1] or item[2] > currentLimits[0][2]:
                currentLimits[0] = [int(item[0]), int(item[1]), int(item[2])]
            elif item[0] < currentLimits[1][0] or item[1] < currentLimits[1][1] or item[2] < currentLimits[1][2]:
                currentLimits[1] = [int(item[0]), int(item[1]), int(item[2])]

            # Update File
            self.writeCalibrationToFile()

            self.updateLimitsText()

    def writeCalibrationToFile(self):
        self.file = open("color_calibration.txt", "w")
        for key, item in self.calibrated_color_limits.items():
            self.file.write(f"{key}-{item[0][0]},{item[0][1]},{item[0][2]}-{item[1][0]},{item[1][1]},{item[1][2]}\n")

        self.file.close()

# MAIN PROGRAM RUNNING CODES
if __name__ == "__main__":
    try:
        # These must be adjusted depending on the device the the program is running on
        # Use the ArduinoIDE to find the ports for the arduino's
        # The camera ID is usually 0 or 1 on windows and /dev/video0 on the Jetson Nano
        cameraID = 0 # /dev/video0
        leftArduino = ArduinoSim() # Arduino("COM5")
        rightArduino = ArduinoSim() # Arduino("COM6")

        displayHeight = 640
        displayWidth = 800

        motionTracker = MotionTracker(leftArduino, rightArduino)

        # The color calibration window is likely temporary and thus so is the way that the app is run.
        colorCalibration = ColorCalibrationWindow()

        app = App(cameraID, motionTracker, colorCalibration, displayHeight, displayWidth)

        colorCalibration.connectApp(app=app)
        colorCalibration.run()

    except KeyboardInterrupt:
        # Catch the keyboard interrupt to end the program gracefully
        print("KI")
    except:
        print("OTHER")
        import traceback
        traceback.print_exc()
    try:    
        print("Closing Connections")
        app.motionTracker.stop()
        app.AR.release()
        cv2.destroyAllWindows()
        
    except:
        pass
    print("ENDED")
