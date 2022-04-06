# OpenCV
import cv2
# Numpy
import numpy as np
#  Serial
from pySerialTransfer import pySerialTransfer as txfer
# Threading
import threading
# Other Improts
from datetime import datetime, timedelta
from random import randint
import time

class movementTracking():
   def __init__(self):
        pass

class ArduinoData(object):
       millisSince = 0
       yaw = 0.0 #yaw
       pitch = 0.0 #pitch
        
class Arduino():
    def __init__(self, serialPort):
        self.serialPort = serialPort
        self.data = ArduinoData()
        self.serial = None

        self.connectSerial()

    def connectSerial(self):
        try:
            self.serial = txfer.SerialTransfer(self.serialPort)
            self.serial.open()
            time.sleep(2)

        except:
            import traceback
            traceback.print_exc()
            print("LINK")
            
            try:
                self.serial.close()
            except:
                print("LINK 2")
                pass
        
    def readData(self):
        print("Reading Data")
        if self.serial.available():
            print("Avaliable")
            recSize = 0
            
            self.data.millisSince = self.serial.rx_obj(obj_type='i', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['i']   
            
            self.data.yaw = self.serial.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
            
            self.data.pitch = self.serial.rx_obj(obj_type='f', start_pos=recSize)
            recSize += txfer.STRUCT_FORMAT_LENGTHS['f']
            print("Reading Worked")
            
        elif self.serial.status < 0:
            print("Error")
            if self.serial.status == txfer.CRC_ERROR:
                print('ERROR: CRC_ERROR')
            elif self.serial.status == txfer.PAYLOAD_ERROR:
                print('ERROR: PAYLOAD_ERROR')
            elif self.serial.status == txfer.STOP_BYTE_ERROR:
                print('ERROR: STOP_BYTE_ERROR')
            else:
                print('ERROR: {}'.format(self.serial.status))


        print("Done Reading")

class AR():

    def __init__(self, app):
        self.app = app
        # Variables
        self.prev_frame_time = time.time()
        self.start_time = 0
        self.end_time = 0
        self.state = "menu"

        # Settings
        self.video_capture = cv2.VideoCapture(0)
        self.max_frame_rate = 60
        self.DISPLAY_HEIGHT = 1000
        self.DISPLAY_WIDTH = 1900

    def release(self):
        self.video_capture.release()

    def addText(self, image, text, location="C", color=(0,0,255), scale=1, thickness=2, margin=40):
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
        else:
            start_x = self.DISPLAY_WIDTH/2 - txt_size[0][0]/2
            start_y = self.DISPLAY_HEIGHT/2 + txt_size[0][1]/2
            pos = (int(start_x), int(start_y))

        cv2.putText(image, text, pos, font_face, scale, color, thickness, cv2.LINE_AA, False)
       
    def demoProgram(self):
        self.video_capture = cv2.VideoCapture(0)
        cv2.namedWindow("Laparoscopic Surgery Training Module") # Create a named window
        cv2.moveWindow("Laparoscopic Surgery Training Module", 5, 5)  # Move it to (5,5)
        cv2.setMouseCallback("Laparoscopic Surgery Training Module", self.onMouseClick)
        print("Starting Demo Program")

        while not self.state == "quit":
            if self.app.keyboardInput == "q":
                print("Quitting")
                self.app.keyboardInput = ""
                self.state = "quit"
            elif self.app.keyboardInput == "a" and self.state == "menu":
                print("Changing State to Running")
                self.app.keyboardInput = ""
                self.state = "running"
                self.start_time = time.time()
            elif self.app.keyboardInput == "a" and self.state == "running":
                print("Changing State to Evaluation")
                self.app.keyboardInput = ""
                self.state = "evaluation"
                self.end_time = time.time()
            elif self.app.keyboardInput == "b" and self.state == "evaluation":
                print("Changing State to Menu")
                self.app.keyboardInput = ""
                self.state = "menu"
                
            if self.state == "menu":
                ret, image = self.video_capture.read()
                image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
                h, w, other = image.shape
                black = np.zeros([h, w, 3], np.uint8)

                self.addText(black, f"Main Menu", "C", scale=3)
                self.addText(black, f"Start Ring Task", "TL")
                self.addText(black, f"Start Wire Task", "TR")
                self.addText(black, f"Tutorial", "BL")
                self.addText(black, f"Evaluation", "BR")
                
                cv2.imshow('Laparoscopic Surgery Training Module', black)

            elif self.state == "running":
                #self.app.rightArduino.readData()
                #print(self.app.rightArduino.data.yaw)

                time_elapsed = time.time() - self.prev_frame_time
                #print(f"{time_elapsed} > {1/self.max_frame_rate}?")
                if time_elapsed > 1/self.max_frame_rate:
                    # Actual FPS calc
                    new_frame_time = time.time()
                    print(f"Time Since Last Frame: {new_frame_time-self.prev_frame_time}")
                    fps = 1/(new_frame_time-self.prev_frame_time)
                    self.prev_frame_time = new_frame_time
                    fps = int(fps)

                    time_since_start = int(time.time()-self.start_time)
                    ret, image = self.video_capture.read()
                    image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
                    self.addText(image, f"Time (s): {time_since_start}", "BR")
                    self.addText(image, f"Yaw: {'Test'}, Pitch: {'Test'}", "BR") #self.app.rightArduino.data.yaw #self.app.rightArduino.data.pitch
                    cv2.imshow('Laparoscopic Surgery Training Module', image)

            elif self.state == "evaluation":
                ret, image = self.video_capture.read()
                image = cv2.resize(image, (self.DISPLAY_WIDTH, self.DISPLAY_HEIGHT))
                h, w, other = image.shape
                black = np.zeros([h, w, 3], np.uint8)

                self.addText(black, f"Task Completed in {int(self.end_time-self.start_time)} seconds", scale=1)
                self.addText(black, f"Back to Main Menu", "BL")
                self.addText(black, f"Quit", "BR")

                cv2.imshow('Laparoscopic Surgery Training Module', black)
            cv2.waitKey(1)

    def onMouseClick(self, event, x, y, flags, param):
        #print(event)
        if event == cv2.EVENT_LBUTTONDOWN:
            print((x,y))
            if y < self.DISPLAY_HEIGHT/2 and x < self.DISPLAY_WIDTH/2:
                # Top Left
                self.app.keyboardInput = "a"
            elif y < self.DISPLAY_HEIGHT/2 and x > self.DISPLAY_WIDTH/2:
                # Top Right
                self.app.keyboardInput = "a"
            elif y > self.DISPLAY_HEIGHT/2 and x < self.DISPLAY_WIDTH/2:
                # Bottom Left
                self.app.keyboardInput = "b"
            elif y > self.DISPLAY_HEIGHT/2 and x > self.DISPLAY_WIDTH/2:
                # Bottom Right
                self.app.keyboardInput = "q"

class App():
    def __init__(self):
        self.rightArduino = Arduino("COM5")
        self.AR = AR(self)
        self.keyboardInput = ""
        

    def run(self):
        self.AR.demoProgram()

def getUserInputThread(app):
   while True:
       app.keyboardInput = input("Enter a command (a, q, or b): ")

if __name__ == "__main__":
    app = None
    try:
        app = App()
        t1 = threading.Thread(target=getUserInputThread, args=(app,))
        t1.start()
        app.run()

    except KeyboardInterrupt:
        print("KI")

    except:
        print("OTHER")
        import traceback
        traceback.print_exc()
        
    app.AR.release()
    cv2.destroyAllWindows()
    print("ENDED")