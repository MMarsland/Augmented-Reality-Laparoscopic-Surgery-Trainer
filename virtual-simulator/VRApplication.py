import bpy
from mathutils import Matrix
import serial
import time
import math
import csv
import os
from datetime import datetime

import random
keyboard = True
try:
    import keyboard
except Exception:
    print("No Keyboard Module Found")
    keyboard = False

class ExitOK(Exception):
    pass

class Tool():
    def __init__(self, name, cpi=1600, blenderConversion=1000, tool_diameter=5, yawOffset=0, pitchOffset=0, rollOffset=0, surgeOffset=0):
        self.tool = bpy.context.scene.objects[name]
        self.rollCount = 0
        self.surgeCount = 0
        self.tool_diameter = tool_diameter
        self.cpi = cpi
        self.blenderConversion = blenderConversion
        
        self.yawOffset = yawOffset
        self.pitchOffset = pitchOffset
        self.rollOffset = rollOffset
        self.surgeOffset = surgeOffset
        
        self.rollCountOffset = 0
        self.surgeCountOffset = 0
        
    def updatePosition(self, data):
        self.rollCount = data["rollCount"]
        self.surgeCount = data["surgeCount"]
        
        rollAngle = (self.rollCount+self.rollCountOffset) / self.cpi * 25.4 * 2 / self.tool_diameter #roll angle in radians (counts*(inch/counts)*(mm/inch)*(radians/mm) = radians
        surge = (self.surgeCount+self.surgeCountOffset) / self.cpi * 25.4  # Surge in mm (counts*(inch/counts)*(mm/inch) = mm)
        blenderSurge = (surge+self.surgeOffset)/self.blenderConversion
        
        # May need to adjust 'X', 'Y', 'Z', and blenderSurge positions here based on blender axis
        rot_yaw = Matrix.Rotation((data["yawAngle"]+self.yawOffset)*math.pi/180, 4, 'Y')
        rot_pitch = Matrix.Rotation((-data["pitchAngle"]+self.pitchOffset)*math.pi/180, 4, 'X')
        rot_roll = Matrix.Rotation((-rollAngle+self.rollOffset), 4, 'Y')
        trans_surge = Matrix.Translation((0,blenderSurge,0))

        loc = Matrix.Translation((0,0,0))
        self.tool.matrix_world = loc
        self.tool.matrix_world = rot_pitch @ self.tool.matrix_world
        self.tool.matrix_world = rot_yaw @ self.tool.matrix_world 
        self.tool.matrix_world = self.tool.matrix_world @ rot_roll
        self.tool.matrix_world = self.tool.matrix_world @ trans_surge
    
class App():
    def __init__(self, tool, interval):
        self.check_block = bpy.context.scene.objects["check"]
        self.check_block.location = (0.5,random.randint(0,1000000)/10000000, 0)
        self.check_block_location = f"{self.check_block.location}"
        self.id = random.randint(0,100)
        
        self.tool = tool
        self.interval = interval
        
        self.useSerial = False
        self.arduino = None
        self.simDataIndex = 0
        self.mpuData = []
        self.pmwData = []
        
    def close(self):
        print("Closing Arduino")
        self.arduino.close()
        
    def setupDataConnection(self, useSerial, com, boderate):
        self.useSerial = useSerial
        if (self.useSerial):
            self.arduino = serial.Serial(com, serialBodeRate, timeout=1)
            time.sleep(2)
        else:
            with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/mpuExampleData.csv") as csvfile:
                rdr = csv.reader( csvfile )
                for i, row in enumerate(rdr):
                    self.mpuData.append(row)
            
            with open(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))+"/pmwExampleData.csv") as csvfile:
                rdr = csv.reader( csvfile )
                for i, row in enumerate(rdr):
                    if i == 0:
                        pass
                    else:
                        self.pmwData.append(row)
    
    # Data form for now:
    # Data:yaw:pitch:roll:surge # UNITS: string:degrees:degrees:counts:counts           
    def parseData(self, data):
        yawAngle = 0
        pitchAngle = 0
        rollAngle = 0
        rollCount = 0
        surgeCount = 0
        
        try:
            if (data[0:5] == "Data:"):
                data = data[5:-2]
                dataArr = data.split(":")
                if (len(dataArr) > 0):
                    yawAngle = float(dataArr[1])
                if (len(dataArr) > 1):
                    pitchAngle = float(dataArr[4].split("=")[1])
                if (len(dataArr) > 2):
                    pass
                    #rollAngle = float(dataArr[2].split("=")[1])
                if (len(dataArr) > 3):
                    pass
                    #rollCount += float(dataArr[3].split("=")[1])
                if (len(dataArr) > 4):
                    pass
                    #surgeCount += float(dataArr[4].split("=")[1])    
            else:
                raise Exception("Not Data")
            
        except Exception as e:
            print(f"Error Reading Data: {e}")
            pass
        f.write(f"{datetime.now()},{yawAngle},{pitchAngle},{rollCount},{surgeCount}")
        return {"yawAngle": yawAngle, 
                "pitchAngle": pitchAngle, 
                "rollAngle": rollAngle, 
                "rollCount": rollCount, 
                "surgeCount": surgeCount}
    
    # Read Data from example Data
    def getNextSimData(self):
        
        mpuDataPt = self.mpuData[self.simDataIndex]
        pmwDataPt = self.pmwData[self.simDataIndex]
        data0 = float(mpuDataPt[1]) # angle data should be passed in degrees
        data1 = float(mpuDataPt[3]) # angle data should be passed in degrees
        data2 = pmwDataPt[0] # Pmw data passed in raw counts (Current counts)
        data3 = pmwDataPt[1] # Pmw data passed in raw counts
        dataString = f"Data:{data0}:{data1}:{data2}:{data3}"
        self.simDataIndex += 1
        self.simDataIndex = self.simDataIndex % min(len(self.mpuData), len(self.pmwData))
        if (self.simDataIndex == 0):
            self.tool.rollCount = 0
            self.tool.surgeCount = 0
            
        return dataString
            
            
    def run(self):
        # Check we are still the only one running
        if (not (f"{self.check_block.location}" == self.check_block_location)):
            print("Other Program running, killing self")
            bpy.app.timers.unregister(timer)
            if(self.useSerial):
              self.arduino.close()
            return None
         # Check if exit key is pressed
        if (keyboard and keyboard.is_pressed("q")):
            print("Exit Pressed, killing self")
            bpy.app.timers.unregister(timer)
            if(self.useSerial):
              self.arduino.close()
            global f
            f.close()
            return None
         # Reset Roll and Surge
        if (keyboard and keyboard.is_pressed("r")):
            print("Resetting Roll and Surge")
            self.tool.rollCountOffset = -self.tool.rollCount
            self.tool.surgeCountOffset = -self.tool.surgeCount
        
        #print(f"{self.id}: Running!")
        dataString = ""
        # Read Data Line
        if (useSerial):
            if (not (self.arduino.inWaiting() == 0)):
                line = self.arduino.readline()   # read a byte
                dataString = line.decode()  # convert the byte string to a unicode string
            else:
                print("No Data, Returning")
                return self.interval
        else:
            dataString = self.getNextSimData()


        print(f"DataString: {dataString}")
        
        # Parse Data
        data = self.parseData(dataString)
        #print(data)
        # Update Tool Position
        tool.updatePosition(data)
        
        return self.interval
    
app = None
def timer():
    global app
    return app.run()

f = open("C:/Users/mmars/Downloads/sampleData.txt", "w")
    
if __name__ == "__main__":
    try:
        print("Starting")
        
        #---Axis Test---
        #tool = bpy.context.scene.objects["tool"]
        #loc = Matrix.Translation((0,0,0))
        #tool.matrix_world = loc
        #rot_pitch = Matrix.Rotation(-0.92, 4, 'X')
        #tool.matrix_world = rot_pitch @ tool.matrix_world
        #rot_yaw = Matrix.Rotation(1.0, 4, 'Z')
        #tool.matrix_world = rot_yaw @ tool.matrix_world 
        #rot_roll = Matrix.Rotation(0.8, 4, 'Y')
        #tool.matrix_world = tool.matrix_world @ rot_roll
        #raise ExitOK
        
        
        # Settings
        useSerial = True
        serialBodeRate = 115200
        com = 'COM6'
        
        cpi = 1200 # 1200 count per inch (This is not the correct value but mimics the bad urge data the closeset)
        blenderConversion = 1000 # 1unit:1000mm
        yawOffset = 0 # degrees
        pitchOffset = -90 # degrees
        rollOffset = 0 # degrees
        surgeOffset = -10 #mm 
        
        interval = 0.01
        
        tool = Tool("tool", cpi, blenderConversion, yawOffset=yawOffset, pitchOffset=pitchOffset, rollOffset=rollOffset, surgeOffset=surgeOffset)
        
        app = App(tool, interval)
        app.setupDataConnection(useSerial, com, serialBodeRate)
        
        # Start Timer:
        bpy.app.timers.register(timer)
            
    except ExitOK:
        print("Exiting")
    except Exception as e:
        app.close()
        print("Stopping")
        raise e
        
        
    