'''This file contains the classes for tracking the motion of the tools

This includes the MotionTracker and Tool classes. The motion tracker class tracks the tools
as individual threads and can return information about the tools.

The tool class currently handles writing to the data files individually on their own threads.

@Author: Michael Marsland
@Date: April 2022
'''


class MotionTracker():
    def __init__(self, leftArduino, rightArduino):

        self.leftTool = Tool(self, "left", leftArduino, daemon=True)
        self.leftTool.start()
        self.rightTool = Tool(self, "right", rightArduino, daemon=True)
        self.rightTool.start()

        self.stop = False
        self.writing = False

    def getWarning(self):
        # Return some tells from the tools current values (This is rudimentary)
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
        
        self.data = self.arduino.data
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

                    # If writing state changed
                    if (self.motionTracker.writing != self.writing):
                        self.writing = self.motionTracker.writing
                        if self.writing:
                            self.openFile()
                        elif not self.writing:
                            self.closeFile()

                    # Save new data to file
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
