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
import colorsys

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
            print("LINK")
            
            try:
                self.serial.close()
            except:
                print("LINK 2")
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

    def __init__(self, app, cameraID):
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
        self.DISPLAY_HEIGHT = 800
        self.DISPLAY_WIDTH = 1520

        self.warningFrames = 0
        self.currentWarning = ""

        self.unmodified_color_dict_HSV = {'black': [[255, 255, 105], [0, 0, 0]],
                                        'white': [[180, 18, 255], [0, 0, 231]],
                                        'red1': [[180, 255, 255], [159, 50, 70]],
                                        'red2': [[9, 255, 255], [0, 50, 70]],
                                        'green': [[89, 255, 255], [36, 50, 70]],
                                        'blue': [[128, 255, 255], [90, 50, 70]],
                                        'yellow': [[35, 255, 255], [25, 50, 70]],
                                        'purple': [[158, 255, 255], [129, 50, 70]],
                                        'orange': [[24, 255, 255], [10, 50, 70]],
                                        'gray': [[180, 18, 230], [0, 0, 40]]}

        self.color_dict_HSV = {'black': [[255, 255, 105], [0, 0, 0]],
                                'white': [[180, 18, 255], [0, 0, 231]],
                                'red1': [[180, 255, 255], [159, 50, 70]],
                                'red2': [[9, 255, 255], [0, 50, 70]],
                                'green': [[89, 125, 120], [25, 50, 60]],
                                'blue': [[128, 255, 255], [90, 50, 70]],
                                'yellow': [[35, 255, 255], [15, 80, 100]],
                                'purple': [[158, 255, 255], [129, 50, 70]],
                                'orange': [[24, 255, 255], [10, 50, 70]],
                                'gray': [[180, 18, 230], [0, 0, 40]]}

        self.color_dict_HSV = self.unmodified_color_dict_HSV     

    def release(self):
        self.video_capture.release()
        #self.out.release()

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

                # Start Writing Data to File
                self.app.motionTracker.startWriting()

                # Start Video File
                self.out = cv2.VideoWriter(f'ringTask-{self.start_time}.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 15, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
            elif self.app.keyboardInput == "tr":
                print("Changing State to wireTask")
                self.app.keyboardInput = ""
                self.state = "wireTask"
                self.start_time = time.time()

                # Start Writing Data to File
                self.app.motionTracker.startWriting()
                # Start Video File
                self.out = cv2.VideoWriter(f'wireTask-{self.start_time}.avi', cv2.VideoWriter_fourcc('M','J','P','G'), 15, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

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

        elif self.state == "wireTask":
            if (self.app.keyboardInput == "tr"):
                print("Changing State to Evaluation")
                self.app.keyboardInput = ""
                self.state = "evaluation"
                self.end_time = time.time()
                # Stop Writing to File
                self.app.motionTracker.stopWriting()

                # Stop Video

        elif self.state == "evaluation":
            if self.app.keyboardInput == "bl":
                print("Changing State to Menu")
                self.app.keyboardInput = ""
                self.state = "menu"
            elif self.app.keyboardInput == "br":
                print("Opening Analysis")
                self.app.keyboardInput = ""

                # Open Analysis Windows
                self.app.analyzer.analyze(self.app.motionTracker.leftTool.fileName)
                self.app.analyzer.analyze(self.app.motionTracker.rightTool.fileName)

        elif self.state == "tutorial":
            if self.app.keyboardInput == "bl":
                print("Changing State to Menu")
                self.app.keyboardInput = ""
                self.state = "menu"
            elif self.app.keyboardInput == "tr":
                print("Changing State to Ring Task Tutorial Video")
                self.app.keyboardInput = ""
                self.state = "ringTaskDemo"
                self.tutorialVideoCapture = cv2.VideoCapture("ringTaskDemo.avi")
            elif self.app.keyboardInput == "tl":
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
            self.ringTaskDemoState()
        elif self.state == "wireTaskDemo":
            self.wireTaskDemoState()

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
            self.warningFrames = 10 # When a warning occours, show for 45 frames
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
            
            if self.state == "ringTaskState":
                if time.time() - self.start_time < 30:
                    self.replaceColor(image, 'red2', (0,255,0))
                elif time.time() - self.start_time < 60:
                    self.replaceColor(image, 'green', (0,255,0))

                if time.time() - self.start_time < 10:
                    self.addGuidingText("Move The Ring to The Peg", image)

                # Modify the image based on the data
                if self.warningFrames > 0:
                    self.warningFrames = self.warningFrames - 1
                    if "Vel" in self.currentWarning:
                        self.replaceColor(image, 'yellow', (255,0,0))
                        self.addText(image, f"{self.currentWarning}", "T")
                        self.addWarningText("SLOW DOWN", image)
                    elif "Acc" in self.currentWarning:
                        self.replaceColor(image, 'yellow', (255,0,0))
                        self.addText(image, f"{self.currentWarning}", "T")
                        self.addWarningText("SLOW DOWN", image)

                    self.addText(image, f"Ring Task", "TL")

            else: #wireTaskState
                # Modify the image based on the data
                if self.warningFrames > 0:
                    self.warningFrames = self.warningFrames - 1
                    self.replaceColor(image, 'black', (255,0,0))
                    self.addText(image, f"{self.currentWarning}", "T")
                    self.addWarningText("SLOW DOWN", image)

                self.addText(image, f"Wire Task", "TL")
            
            # Modify the image with other text
            self.addText(image, f"Time (s): {time_since_start}", "BR")

            self.addText(image, f"Complete", "TR")
            self.addText(image, f"Connected: [{'Y' if self.app.motionTracker.leftTool.data.yaw != 0 else 'N'},{'Y' if self.app.motionTracker.rightTool.data.yaw != 0 else 'N'}]", "BL")

            self.out.write(image)
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

    def ringTaskDemoState(self):
        if (self.tutorialVideoCapture.isOpened()):
            ret, image = self.tutorialVideoCapture.read()
            if ret == True:
                image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))

                self.addText(image, f"Back", "BR")

                cv2.imshow('Laparoscopic Surgery Training Module', image)
                return
        
        self.app.keyboardInput = "br"

    def run(self):
        self.video_capture = cv2.VideoCapture(self.cameraID)
        cv2.namedWindow("Laparoscopic Surgery Training Module") # Create a named window
        cv2.moveWindow("Laparoscopic Surgery Training Module", 5, 5)  # Move it to (5,5)
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
            print(f"REAL HSV: {hsv_image[y,x]}")

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
       
    # def addBlackToRedColorContour(self, image):
    #     # COLOR DETECTION BASED ON HSV (Needs to be calibrated)

    #     lowerLimit = np.array(self.color_dict_HSV.get('black')[1])
    #     upperLimit = np.array(self.color_dict_HSV.get('black')[0])

    #     hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #     # find the colors within the specified boundaries and apply
    #     # the mask
    #     mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)

    #     color = (0, 0, 255)

    #     image[(mask==255)] = color

    #     # Display the resulting frame
    #     return image

    # def addYellowToRedColorContour(self, image):
    #     # COLOR DETECTION BASED ON HSV (Needs to be calibrated)

    #     lowerLimit = np.array(self.color_dict_HSV.get('yellow')[1])
    #     upperLimit = np.array(self.color_dict_HSV.get('yellow')[0])

    #     hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #     # find the colors within the specified boundaries and apply
    #     # the mask
    #     mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)

    #     color = (0, 0, 255)

    #     image[(mask==255)] = color

    #     # Display the resulting frame
    #     return image

    # def addRedToGreenColorContour(self, image):
    #     # COLOR DETECTION BASED ON HSV (Needs to be calibrated)

    #     lowerLimit = np.array(self.color_dict_HSV.get('red2')[1])
    #     upperLimit = np.array(self.color_dict_HSV.get('red2')[0])

    #     hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #     # find the colors within the specified boundaries and apply
    #     # the mask
    #     mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)

    #     color = (0, 255, 0)

    #     image[(mask==255)] = color

    #     # Display the resulting frame
    #     return image

    # def addGreenToGreenColorContour(self, image):
    #     # COLOR DETECTION BASED ON HSV (Needs to be calibrated)

    #     lowerLimit = np.array(self.color_dict_HSV.get('green')[1])
    #     upperLimit = np.array(self.color_dict_HSV.get('green')[0])

    #     hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    #     # find the colors within the specified boundaries and apply
    #     # the mask
    #     mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)

    #     color = (0, 255, 0)

    #     image[(mask==255)] = color

    #     # Display the resulting frame
    #     return image

    def replaceColor(self, image, originalColorName, newColor):
        # COLOR DETECTION BASED ON HSV (Needs to be calibrated)

        lowerLimit = np.array(self.color_dict_HSV.get(originalColor)[1])
        upperLimit = np.array(self.color_dict_HSV.get(originalColor)[0])

        hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

        # find the colors within the specified boundaries and apply the mask
        mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)

        image[(mask==255)] = newColor

        # Display the resulting frame
        return image

    def addWarningText(self, text, image):

        color = (0, 0, 255)
    
        self.addText(image=image, text=text, location="B", color=color, scale=2, thickness=2, margin=40)
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
        print(f"Inatalizing tool: {name}")
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
        self.fileName = f"dataFiles/data-{self.name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}"
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
    def __init__(self, cameraID, motionTracker):
        self.motionTracker = motionTracker

        self.AR = AR(self, cameraID)
        self.keyboardInput = ""
        self.analyzer = Analyzer()

    def run(self):
        self.AR.run()


# MAIN PROGRAM RUNNING CODE
if __name__ == "__main__":
    try:
        cameraID = 0
        leftArduino = Arduino("COM5") #ArduinoSim()
        rightArduino = Arduino("COM6") #ArduinoSim()

        motionTracker = MotionTracker(leftArduino, rightArduino)

        app = App(cameraID, motionTracker)
        app.run()

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



# TODO: Combine States (Ring task and Wire Task)
# TODO: Combine color contours into one method
# TODO: Add live color calibration!