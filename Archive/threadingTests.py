import time
from datetime import datetime
import threading
import random

class MotionTracker():
    def __init__(self, leftArduino, rightArduino):

        self.leftTool = Tool(self, "left", leftArduino, daemon=True)
        self.leftTool.start()
        self.rightTool = Tool(self, "right", rightArduino, daemon=True)
        self.rightTool.start()

        self.stop = False
        self.writing = False

    def getWarningLevel(self):
        # Return some tells from the tools current values
        #if (random.randint(0,100) == 0):
        #    return 1
        #return 0
        #print(f"{self.rightTool.data.pitch}")

        # FOR NOW just if right tool pitch > 30
        if (self.rightTool.data.pitchVel > 10):
            return 1
        return 0

    def stop(self):
        # Kills the tool threads
        print("Stopping Motion Tracker")
        self.stop = True

class Tool(threading.Thread):
    def __init__(self, motionTracker, name, arduino, *args, **kwargs):
        super(Tool, self).__init__(*args, **kwargs)
        self.motionTracker = motionTracker
        self.arduino = arduino
        self.name = name

        self.data = MotionData()
        self.writing = False
        self.file = None

    def run(self):
        self.readArduino()

    def openFile(self):
        self.file = open(f"data-{self.name}-{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}", "w")
        self.file.write(f"time,yaw,pitch,roll,surge\n")

    def closeFile(self):
        self.file.close()

    def saveData(self):
        self.file.write(f"{self.data.timeSinceStart},{self.data.yaw},{self.data.pitch},{0},{0}\n")

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
        self.motionTracker.writing = False
        self.writing = False
        self.file.close()

class ArduinoSim():
    def __init__(self):
        self.data = MotionData()
        
        self.startTimeMillis = time.time() * 1000
        
        self.previousTime = time.time()
    
    def connectSerial(self):
        print(f"Sim connect()")
    
    def closeSerial(self):
        print(f"Sim close()") 

    def readData(self):
        #print("Reading Data")
        timeDifMillis = (time.time() - self.previousTime) * 1000
        if (timeDifMillis > 100):
            self.previousTime = time.time()

            self.data.timeSinceStart = time.time() * 1000 - self.startTimeMillis
            self.data.yaw = self.data.yaw + round(random.random()*10 - 5, 0)
            self.data.pitch = self.data.pitch + round(random.random()*10 - 5, 0)
            #self.data.surge = self.data.surge + round(random.random()*10 - 5, 0)
            #print("Returning True")
            return True

        return False

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

if __name__ == "__main__":
    leftArduino = ArduinoSim()
    rightArduino = ArduinoSim()

    mt = MotionTracker(leftArduino, rightArduino)
    
    time.sleep(3)
    mt.writing = True

    time.sleep(3)
    print(f"Data: {mt.rightTool.data.timeSinceStart}:{mt.rightTool.data.yaw}:{mt.rightTool.data.yawVel}:{mt.rightTool.data.yawAcc}:{mt.rightTool.data.pitch}")

    mt.writing = False
    time.sleep(2)

    mt.stop = True