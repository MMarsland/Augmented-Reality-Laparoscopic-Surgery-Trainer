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

# Import Analyzer from Rahme
from analyzer import Analyzer

class MotionData(object):
    timeSinceStart = 0
    yaw = 0.0
    pitch = 0.0
    surge = 0.0

    yawVel = 0.0
    pitchVel = 0.0
    surgeVel = 0.0

    yawAcc = 0.0
    pitchAcc = 0.0
    surgeAcc = 0.0

class Arduino():
    def __init__(self, serialPort):
        self.serialPort = serialPort
        self.data = MotionData()
        self.serial = None

        self.connectSerial()

    def connectSerial(self):
        try:
            self.serial = serial.Serial(self.serialPort, "115200", timeout=1)
            time.sleep(1)
        except:
            import traceback
            traceback.print_exc()     
            try:
                self.serial.close()
            except:
                pass

    def closeSerial(self):
        print("Closing Serial")
        self.serial.close()
        
    def readData(self):
        dataString = None
        if (not (self.serial.inWaiting() == 0)):
            line = self.serial.readline()   # read a byte
            dataString = line.decode()  # convert the byte string to a unicode string
        
        if (dataString and len(dataString) > 0 and dataString[0] == "D"):
            dataString = dataString[0:-2]
            #print(dataString)
            dataArray = dataString.split(":")
            #print(dataArray)
            self.data.timeSinceStart = float(dataArray[1])

            self.data.yaw = float(dataArray[2])
            self.data.yawVel = float(dataArray[3])
            self.data.yawAcc = float(dataArray[4])

            self.data.pitch = float(dataArray[5])
            self.data.pitchVel = float(dataArray[6])
            self.data.pitchAcc = float(dataArray[7])

            self.data.surge = float(dataArray[8])
            self.data.surgeVel = float(dataArray[9])
            self.data.surgeAcc = float(dataArray[10])

            return True
        return False

class ArduinoSim():
    def __init__(self):
        self.data = MotionData()
        self.data.surge = 180
        
        self.startTimeMillis = time.time() * 1000
        
        self.previousTime = time.time()
    
    def connectSerial(self):
        print(f"Sim connect()")
    
    def closeSerial(self):
        print(f"Sim close()") 

    def readData(self):
        timeDifMillis = (time.time() - self.previousTime) * 1000
        if (timeDifMillis > 100):
            self.previousTime = time.time()

            self.data.timeSinceStart = time.time() * 1000 - self.startTimeMillis
            self.data.yaw = self.data.yaw + round(random.random()*10 - 5, 0)
            self.data.pitch = self.data.pitch + round(random.random()*10 - 5, 0)
            self.data.surge = self.data.surge + round(random.random()*10 - 5, 0)
            return True

        return False


# CV2 GUI CLASS
class AR():

    def __init__(self, app, cameraID, height, width):
        self.app = app
        self.cameraID = cameraID

        # Variables
        self.prev_frame_time = time.time()
        self.start_time = 0
        self.end_time = 0
        self.state = "menu"

        # Settings
        self.video_capture = cv2.VideoCapture(0)
        self.max_frame_rate = 15
        self.DISPLAY_HEIGHT = height
        self.DISPLAY_WIDTH = width

        self.warningFrames = 0
        self.currentWarning = ""

    def release(self):
        self.video_capture.release()
        self.videoRecording.release()
        self.tutorialVideoCapture.release()
        

    def evaluateState(self):
        if self.app.keyboardInput == "q":
            print("Quitting")
            self.app.keyboardInput = ""
            self.state = "quit"

        elif self.state == "menu":
            if (self.app.keyboardInput == "tl"):
                print("Changing State to ringTask")
                self.app.keyboardInput = ""
                self.state = "ringTask"
                self.start_time = time.time()
                self.guidanceState = 0

                # Start Writing Data to File
                self.app.motionTracker.startWriting()

                # Start Video File
                self.videoRecording = cv2.VideoWriter(f'videoFiles/ringTask-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 15, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
           
            elif self.app.keyboardInput == "tr":
                print("Changing State to wireTask")
                self.app.keyboardInput = ""
                self.state = "wireTask"
                self.start_time = time.time()

                # Start Writing Data to File
                self.app.motionTracker.startWriting()
                # Start Video File
                self.videoRecording = cv2.VideoWriter(f'videoFiles/wireTask-{datetime.now().strftime("%Y-%m-%d_%H-%M-%S")}.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 15, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

            elif self.app.keyboardInput == "bl":
                self.app.keyboardInput = ""
                self.state = "tutorial"
            elif self.app.keyboardInput == "br":
                print("QUITTING")
                self.app.keyboardInput = "q"

        elif self.state == "ringTask":
            if (self.app.keyboardInput == "tr"):
                print("Changing State to Evaluation")
                self.app.keyboardInput = ""
                self.state = "evaluation"
                self.end_time = time.time()
                # Stop Writing to File
                self.app.motionTracker.stopWriting()

                # Stop Video
                self.videoRecording.release()
            elif (self.app.keyboardInput == "tl"):
                self.app.keyboardInput = ""
                self.guidanceState = self.guidanceState + 1


        elif self.state == "wireTask":
            if (self.app.keyboardInput == "tr"):
                print("Changing State to Evaluation")
                self.app.keyboardInput = ""
                self.state = "evaluation"
                self.end_time = time.time()
                # Stop Writing to File
                self.app.motionTracker.stopWriting()

                # Stop Video
                self.videoRecording.release()

        elif self.state == "evaluation":
            if self.app.keyboardInput == "bl":
                print("Changing State to Menu")
                self.app.keyboardInput = ""
                self.state = "menu"
            elif self.app.keyboardInput == "br":
                print("Opening Analysis")
                self.app.keyboardInput = ""

                # Open Analysis Windows
                self.app.analyzer.analyze(self.app.motionTracker.leftTool.fileName, left=True)
                self.app.analyzer.analyze(self.app.motionTracker.rightTool.fileName, left=False)

        elif self.state == "tutorial":
            if self.app.keyboardInput == "bl":
                print("Changing State to Menu")
                self.app.keyboardInput = ""
                self.state = "menu"
            elif self.app.keyboardInput == "tl":
                print("Changing State to Ring Task Tutorial Video")
                self.app.keyboardInput = ""
                self.state = "ringTaskDemo"
                self.tutorialVideoCapture = cv2.VideoCapture("ringTaskDemo.avi")
            elif self.app.keyboardInput == "tr":
                print("Changing State to Wire Task Tutorial Video")
                self.app.keyboardInput = ""
                self.state = "wireTaskDemo"
                self.tutorialVideoCapture = cv2.VideoCapture("wireTaskDemo.avi")

        elif self.state == "ringTaskDemo":
            if self.app.keyboardInput == "br":
                print("Back to Tutorial State")
                self.app.keyboardInput = ""
                self.state = "tutorial"
                self.tutorialVideoCapture.release()

        elif self.state == "wireTaskDemo":
            if self.app.keyboardInput == "br":
                print("Back to Tutorial State")
                self.app.keyboardInput = ""
                self.state = "tutorial"
                self.tutorialVideoCapture.release()
        
    def displayByState(self):
        if self.state == "menu":
            self.menuState()
        elif self.state == "ringTask":
            self.taskState()
        elif self.state == "wireTask":
            self.taskState()
        elif self.state == "evaluation":
            self.evaluationState()
        elif self.state == "tutorial":
            self.tutorialState()
        elif self.state == "ringTaskDemo":
            self.tutorialVideoState()
        elif self.state == "wireTaskDemo":
            self.tutorialVideoState()

    # DEFINE PROGRAM STATES
    def menuState(self):
        ret, image = self.video_capture.read()
        image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        h, w, other = image.shape
        black = np.zeros([h, w, 3], np.uint8)

        self.addText(black, f"Main Menu", "C", scale=3)
        self.addText(black, f"Start Ring Task", "TL")
        self.addText(black, f"Start Wire Task", "TR")
        self.addText(black, f"Tutorial", "BL")
        self.addText(black, f"Quit", "BR")
        
        self.image = black
        cv2.imshow('Laparoscopic Surgery Training Module', black)

    def taskState(self):
        # Check Motion Tracker
        warning = self.app.motionTracker.getWarning()
        if not warning == "":
            self.warningFrames = 10 # When a warning occurs, show for 45 frames
            self.currentWarning = warning

        time_elapsed = time.time() - self.prev_frame_time
        
        if time_elapsed > 1/self.max_frame_rate:
            # Actual FPS calc
            new_frame_time = time.time()
            fps = 1/(new_frame_time-self.prev_frame_time)
            self.prev_frame_time = new_frame_time
            fps = int(fps)

            time_since_start = int(time.time()-self.start_time)
            ret, image = self.video_capture.read()
            image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            
            # Add Guidance
            if self.state == "ringTask":
                # if time.time() - self.start_time < 30:
                #     self.guidanceState = 0
                # elif time.time() - self.start_time < 60:
                #     self.guidanceState = 1
                if (self.guidanceState == 0):
                    mask = self.replaceColor(image, 'red1', (0,255,0))
                    if (self.centroidsClose(mask)):
                        self.guidanceState = 1
                        print("NEW GUIDANCE STATE UNLOCKED")

                elif (self.guidanceState == 1):
                    mask = self.replaceColor(image, 'green', (0,255,0))
                    if (self.centroidsClose(mask)):
                        self.guidanceState = 2

                elif (self.guidanceState == 2):
                    mask = self.replaceColor(image, 'blue', (0,255,0))
                    if (self.centroidsClose(mask)):
                        self.guidanceState = 3

                elif (self.guidanceState == 3):
                    mask = self.replaceColor(image, 'brown', (0,255,0))
                    if (self.centroidsClose(mask)):
                        self.guidanceState = 4

                if time.time() - self.start_time < 10:
                    self.addGuidingText("Move The Ring to The Peg", image)
                    

            else: #wireTaskState
                imageParts = [image[:,0:round(self.DISPLAY_WIDTH/2-200),:],
                              image[:,round(self.DISPLAY_WIDTH/2-200):round(self.DISPLAY_WIDTH/2+200),:],
                              image[:,round(self.DISPLAY_WIDTH/2+200):round(self.DISPLAY_WIDTH),:]]
                if time.time() - self.start_time < 1:
                    self.replaceColor(imageParts[0], 'black', (0,255,0))
                elif time.time() - self.start_time < 2:
                    self.replaceColor(imageParts[1], 'black', (0,255,0))
                elif time.time() - self.start_time < 3:
                    self.replaceColor(imageParts[2], 'black', (0,255,0))
                elif time.time() - self.start_time < 4:
                    self.replaceColor(imageParts[0], 'black', (0,255,0))
                elif time.time() - self.start_time < 5:
                    self.replaceColor(imageParts[1], 'black', (0,255,0))
                elif time.time() - self.start_time < 6:
                    self.replaceColor(imageParts[2], 'black', (0,255,0))
                elif time.time() - self.start_time < 7:
                    self.replaceColor(imageParts[0], 'black', (0,255,0))
                elif time.time() - self.start_time < 8:
                    self.replaceColor(imageParts[1], 'black', (0,255,0))
                elif time.time() - self.start_time < 9:
                    self.replaceColor(imageParts[2], 'black', (0,255,0))

                if time.time() - self.start_time < 9:
                    self.addGuidingText("Thread the needle", image)
                # Modify the image based on the data

            # Add Warnings
            if self.warningFrames > 0:
                self.warningFrames = self.warningFrames - 1
                replaceColor = 'yellow' if self.state == "ringTask" else 'black'

                if "Vel" in self.currentWarning:
                    self.replaceColor(image, replaceColor, (0,0,255))
                    self.addWarningText(f'Slow {self.currentWarning.replace("-", " ")[:-4]} vel.', image)
                elif "Acc" in self.currentWarning:
                    self.replaceColor(image, replaceColor, (0,180,255))
                    self.addWarningText(f'Decrease {self.currentWarning.replace("-", " ")[:-4]} accel.', image, color=(0,180,255))

            
            # Modify the image with other text
            if self.state == "ringTask":
                self.addText(image, f"Ring Task", "TL")
            else:
                self.addText(image, f"Wire Task", "TL")
            self.addText(image, f"Time (s): {time_since_start}", "BR")
            self.addText(image, f"Complete", "TR")
            self.addText(image, f"Connected: [{'Y' if self.app.motionTracker.leftTool.data.yaw != 0 else 'N'},{'Y' if self.app.motionTracker.rightTool.data.yaw != 0 else 'N'}]", "BL")

            self.videoRecording.write(image)
            self.image = image
            cv2.imshow('Laparoscopic Surgery Training Module', image)

    def evaluationState(self):
        ret, image = self.video_capture.read()
        image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        h, w, other = image.shape
        black = np.zeros([h, w, 3], np.uint8)

        self.addText(black, f"Task Completed in {int(self.end_time-self.start_time)} seconds", scale=1)
        self.addText(black, f"Back to Main Menu", "BL")
        self.addText(black, f"View Analysis", "BR")

        cv2.imshow('Laparoscopic Surgery Training Module', black)

    def tutorialState(self):
        ret, image = self.video_capture.read()
        image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
        h, w, other = image.shape
        black = np.zeros([h, w, 3], np.uint8)

        self.addText(black, f"RING TASK", "TutorialLeft", line=0)
        self.addText(black, f"Move the colored rings", "TutorialLeft", line=1)
        self.addText(black, f"to thier corresponding", "TutorialLeft", line=2)
        self.addText(black, f"peg in order of peg!", "TutorialLeft", line=3)

        self.addText(black, f"WIRE TASK", "TutorialRight", line=0)
        self.addText(black, f"Thread the needle through", "TutorialRight", line=1)
        self.addText(black, f"the loops from top left", "TutorialRight", line=2)
        self.addText(black, f"to bottom right following", "TutorialRight", line=3)
        self.addText(black, f"the arrow.", "TutorialRight", line=4)

        self.addText(black, f"Back to Main Menu", "BL")
        self.addText(black, f"View Ring Task Demo", "TL")
        self.addText(black, f"View Wire Task Demo", "TR")

        cv2.imshow('Laparoscopic Surgery Training Module', black)

    def tutorialVideoState(self):
        if (self.tutorialVideoCapture.isOpened()):
            time_elapsed = time.time() - self.prev_frame_time
        
            if time_elapsed > 1/(self.max_frame_rate*1.25): # Play tutorials at 1.25 speed
                self.prev_frame_time = time.time()
                ret, image = self.tutorialVideoCapture.read()
                if ret == True:
                    image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

                    self.addText(image, f"Back", "BR")

                    cv2.imshow('Laparoscopic Surgery Training Module', image)
                    return
            else:
                return
        
        self.app.keyboardInput = "br"

    def run(self):
        self.video_capture = cv2.VideoCapture(self.cameraID)
        cv2.namedWindow("Laparoscopic Surgery Training Module") # Create a named window
        #cv2.moveWindow("Laparoscopic Surgery Training Module", 0, 0)  # Move it to (5,5)
        cv2.setMouseCallback("Laparoscopic Surgery Training Module", self.onMouseClick)
        print("Starting Demo Program")

        while not self.state == "quit":
           
            self.evaluateState()

            self.displayByState()

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                self.app.keyboardInput = "q"
            elif key == ord('a'):
                self.app.keyboardInput = "tl"
            elif key == ord('b'):
                self.app.keyboardInput = "bl"
            elif key == ord('c'):
                self.app.keyboardInput = "tr"
            elif key == ord('v'):
                self.app.keyboardInput = "br"

    def onMouseClick(self, event, x, y, flags, param):
        #print(event)
        if event == cv2.EVENT_LBUTTONDOWN:
            #print((x,y))
            if y < self.DISPLAY_HEIGHT/2 and x < self.DISPLAY_WIDTH/2:
                # Top Left
                self.app.keyboardInput = "tl"
            elif y < self.DISPLAY_HEIGHT/2 and x > self.DISPLAY_WIDTH/2:
                # Top Right
                self.app.keyboardInput = "tr"
            elif y > self.DISPLAY_HEIGHT/2 and x < self.DISPLAY_WIDTH/2:
                # Bottom Left
                self.app.keyboardInput = "bl"
            elif y > self.DISPLAY_HEIGHT/2 and x > self.DISPLAY_WIDTH/2:
                # Bottom Right
                self.app.keyboardInput = "br"
        if event == cv2.EVENT_RBUTTONDOWN:
            hsv_image = cv2.cvtColor(self.image, cv2.COLOR_BGR2HSV)
            #print(f"REAL HSV: {hsv_image[y,x]}")
            self.app.colorCalibration.addColorToLimit(hsv_image[y,x])

    def addText(self, image, text, location="C", color=(0,0,255), scale=1, thickness=2, margin=40, line=0):
        font_face = cv2.FONT_HERSHEY_SIMPLEX

        pos = None
        txt_size = cv2.getTextSize(text, font_face, scale, thickness)
        if (location == "TL"):
            start_x = margin
            start_y =  txt_size[0][1] + margin
            pos = (int(start_x), int(start_y))
        elif (location == "TR"):
            start_x = self.DISPLAY_WIDTH - txt_size[0][0] - margin
            start_y = txt_size[0][1] + margin
            pos = (int(start_x), int(start_y))
        elif (location == "BL"):
            start_x = margin
            start_y = self.DISPLAY_HEIGHT - margin
            pos = (int(start_x), int(start_y))
        elif (location == "BR"):
            start_x = self.DISPLAY_WIDTH - txt_size[0][0] - margin
            start_y = self.DISPLAY_HEIGHT - margin
            pos = (int(start_x), int(start_y))
        elif (location == "B"):
            start_x = self.DISPLAY_WIDTH/2 - txt_size[0][0]/2
            start_y = self.DISPLAY_HEIGHT - margin
            pos = (int(start_x), int(start_y))
        elif (location == "T"):
            start_x = self.DISPLAY_WIDTH/2 - txt_size[0][0]/2
            start_y = txt_size[0][1] + margin
            pos = (int(start_x), int(start_y))
        elif (location == "TutorialLeft"):
            start_x = self.DISPLAY_WIDTH/2 - txt_size[0][0] - margin
            start_y = self.DISPLAY_HEIGHT/3 + (txt_size[0][1]+20) * line
            pos = (int(start_x), int(start_y))
        elif (location == "TutorialRight"):
            start_x = self.DISPLAY_WIDTH/2 + margin
            start_y = self.DISPLAY_HEIGHT/3 + (txt_size[0][1]+20) * line
            pos = (int(start_x), int(start_y))
        else:
            start_x = self.DISPLAY_WIDTH/2 - txt_size[0][0]/2
            start_y = self.DISPLAY_HEIGHT/2 + txt_size[0][1]/2
            pos = (int(start_x), int(start_y))

        cv2.putText(image, text, pos, font_face, scale, color, thickness, cv2.LINE_AA, False)

    def centroidsClose(self, mask):
        
        # find contours in the binary image
        contours, hierarchy = cv2.findContours(mask,cv2.RETR_TREE,cv2.CHAIN_APPROX_SIMPLE)
        #print(f"Number of contours Found: {len(contours)}")
        centroids = []
        for c in contours:
            #print(c)
            M = cv2.moments(c)
            #print(M)
            #print(f'Area: {M["m00"]}')
            if (M["m00"] > 750):
                # calculate x,y coordinate of center
                #print(f"Finding Center")
                cX = int(M["m10"] / M["m00"])
                cY = int(M["m01"] / M["m00"])
                #cv2.circle(mask, (cX, cY), 5, (255, 255, 255), -1)
                #cv2.putText(mask, "centroid", (cX - 25, cY - 25),cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)
                #print(f"{cX},{cY}")
                centroids.append((cX,cY))
        #cv2.imshow('Mask', mask)
        # Get distance between centroids
        #print(centroids)
        #print(f"Number of centroids Found: {len(centroids)}")
        if len(centroids) >= 3:
            x1 = centroids[0][0]
            x2 = centroids[2][0]
            xDiff = abs(x2-x1)
            y1 = centroids[0][1]
            y2 = centroids[2][1]
            yDiff = abs(y2-y1)
            distance = math.sqrt(xDiff**2 + yDiff**2)
        
            #print(f"Distance: {distance}")

            if distance < 100 and distance > 5:
                return True
        return False
            


    def replaceColor(self, image, originalColorName, newColor): # newColor as BGR
        # COLOR DETECTION BASED ON HSV (Needs to be calibrated)
        #print(f"Replacing {originalColorName} with {newColor}")

        lowerLimit = np.array(self.app.colorCalibration.calibrated_color_limits.get(originalColorName)[1])
        upperLimit = np.array(self.app.colorCalibration.calibrated_color_limits.get(originalColorName)[0])

        #print(f"Lower Limit: {lowerLimit}")
        #print(f"Upper Limit: {upperLimit}")

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # find the colors within the specified boundaries and apply the mask
        mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)

        image[(mask==255)] = newColor

        # Display the resulting frame
        return mask

    def addWarningText(self, text, image, color=(0, 0, 255)):
        self.addText(image=image, text=text, location="B", color=color, scale=1.5, thickness=2, margin=40)
        return image
    
    def addGuidingText(self, text, image):

        color = (0, 255, 0)
    
        self.addText(image=image, text=text, location="B", color=color, scale=2, thickness=2, margin=40)
        return image

# MOTION TRACKER CLASS
class MotionTracker():
    def __init__(self, leftArduino, rightArduino):

        self.leftTool = Tool(self, "left", leftArduino, daemon=True)
        self.leftTool.start()
        self.rightTool = Tool(self, "right", rightArduino, daemon=True)
        self.rightTool.start()

        self.stop = False
        self.writing = False

    def getWarning(self):
        # Return some tells from the tools current values
        if(abs(self.leftTool.data.yawVel) > 20):
            return "Left-Yaw-Vel"
        elif(abs(self.leftTool.data.pitchVel) > 20):
            return "Left-Pitch-Vel"
        elif(abs(self.leftTool.data.surgeVel) > 50):
            return "Left-Surge-Vel"
        elif(abs(self.leftTool.data.yawAcc) > 200):
            return "Left-Yaw-Acc"
        elif(abs(self.leftTool.data.pitchAcc) > 200):
            return "Left-Pitch-Acc"
        elif(abs(self.leftTool.data.surgeAcc) > 500):
            return "Left-Surge-Acc"

        elif (abs(self.rightTool.data.yawVel) > 20):
            return "Right-Yaw-Vel"
        elif(abs(self.rightTool.data.pitchVel) > 20):
            return "Right-Pitch-Vel"
        elif(abs(self.rightTool.data.surgeVel) > 50):
            return "Right-Surge-Vel"
        elif (abs(self.rightTool.data.yawAcc) > 200):
            return "Right-Yaw-Acc"
        elif(abs(self.rightTool.data.pitchAcc) > 200):
            return "Right-Pitch-Acc"
        elif(abs(self.rightTool.data.surgeAcc) > 500):
            return "Right-Surge-Acc"
        return ""

    def startWriting(self):
        self.writing = True

    def stopWriting(self):
        self.writing = False

    def stop(self):
        # Kills the tool threads
        print("Stopping Motion Tracker")
        self.stop = True

class Tool(threading.Thread):
    def __init__(self, motionTracker, name, arduino, *args, **kwargs):
        super(Tool, self).__init__(*args, **kwargs)
        print(f"Initalizing tool: {name}")
        self.motionTracker = motionTracker
        self.name = name
        self.arduino = arduino
        
        self.data = MotionData()
        self.writing = False
        self.file = None
        self.fileName = ""

    def run(self):
        self.readArduino()

    def openFile(self):
        self.fileName = f"dataFiles/data-{self.name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.csv"
        print(f"Writing File: {self.fileName}")
        self.file = open(self.fileName, "w")
        self.file.write(f"time,yaw,yawVel,yawAcc,pitch,pitchVel,pitchAcc,surge,surgeVel,surgeAcc\n")

    def closeFile(self):
        self.file.close()

    def saveData(self):
        self.file.write(f"{self.data.timeSinceStart},{self.data.yaw},{self.data.yawVel},{self.data.yawAcc},{self.data.pitch},{self.data.pitchVel},{self.data.pitchAcc},{self.data.surge},{self.data.surgeVel},{self.data.surgeAcc}\n")

    def readArduino(self):
        time.sleep(1)
        try:
            while not self.motionTracker.stop:
                if (self.arduino.readData()):

                    self.data = self.arduino.data

                    # If writing state changed
                    if (self.motionTracker.writing != self.writing):
                        self.writing = self.motionTracker.writing
                        if self.writing:
                            self.openFile()
                        elif not self.writing:
                            self.closeFile()

                    # Save new Data to file
                    if self.writing:
                        self.saveData()

        except Exception as e:
            print(e)
        self.close()

    def close(self):
        self.arduino.closeSerial()
        self.file.close()
        self.motionTracker.writing = False
        self.writing = False


# MAIN PYTHON APP CLASS
class App():
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

        # self.calibrated_color_limits = {'black': [[255, 255, 105], [0, 0, 0]],
        #                                 'white': [[180, 18, 255], [0, 0, 231]],
        #                                 'red1': [[180, 255, 255], [159, 50, 70]],
        #                                 'red2': [[9, 255, 255], [0, 50, 70]],
        #                                 'green': [[89, 255, 255], [36, 50, 70]],
        #                                 'blue': [[128, 255, 255], [90, 50, 70]],
        #                                 'yellow': [[90, 255, 255], [25, 50, 70]],
        #                                 'purple': [[158, 255, 255], [129, 50, 70]],
        #                                 'orange': [[24, 255, 255], [10, 50, 70]],
        #                                 'gray': [[180, 18, 230], [0, 0, 40]]}

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

        # [[100, 255, 255], [90, 50, 70]]
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
            # Is this done by reference?
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

# MAIN PROGRAM RUNNING CODE
if __name__ == "__main__":
    try:
        cameraID = 0
        leftArduino = Arduino("COM5") #ArduinoSim()
        rightArduino = Arduino("COM6") #ArduinoSim()

        motionTracker = MotionTracker(leftArduino, rightArduino)

        colorCalibration = ColorCalibrationWindow()

        displayHeight = 1040
        displayWidth = 1920 

        app = App(cameraID, motionTracker, colorCalibration, displayHeight, displayWidth)

        colorCalibration.connectApp(app=app)
        colorCalibration.run()

    except KeyboardInterrupt:
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



# TODO: Check / Calibrate Analyzer to match
# TODO: Calibrate Wire Task Guidance
# TODO: Improve live color calibration!