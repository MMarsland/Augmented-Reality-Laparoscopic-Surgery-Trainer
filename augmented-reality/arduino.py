'''This file contains the Arduino, ArduinoSim, and MotionData classes

This file regards the connection to the arduino or arduinos and the
collection of data from the sensors. (or the simulation of such)

@Author: Michael Marsland
@Date: April 2022
'''

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
        
        # Data is currently in the form:
        # "DATA:"+timeSinceStartStr+":"+yawStr+":"+yawVelStr+":"+yawAccStr+":"+pitchStr+":"+pitchVelStr+":"+pitchAccStr+":"+surgeStr+":"+surgeVelStr+":"+surgeAccStr
        if (dataString and len(dataString) > 0 and dataString[0] == "D"):
            dataString = dataString[0:-2] # Cut off new line and carrage return
            dataArray = dataString.split(":")
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
        self.data.surge = 180 # Random Start Value (The usual rest value of the tool)
        
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
