# Tkinter
import tkinter as tk
# Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.dates as mdates
from matplotlib.ticker import MaxNLocator
# CSV Reader
import pandas as pd
# Other
import time
from datetime import datetime, timedelta
import random
import numpy as np

class Plot(tk.Frame):
    def _init_(self, parent, x_data, y_data, label, color, reference_line, vertical_threshold):
        super()._init_(parent)

        # matplotlib figure
        self.figure = Figure(figsize=(22, 5), dpi=58)

        self.ax = self.figure.add_subplot(111)
        # Format the x-axis to show the time
        # myFmt = mdates.DateFormatter("%H:%M:%S.%f")
        # self.ax.xaxis.set_major_formatter(myFmt)
        self.ax.xaxis.set_major_locator(MaxNLocator(30))

        # Set initial x and y data (Null Data)
        #dateTimeObj = datetime.now() + timedelta(seconds=-nb_points)
        #self.x_data = [dateTimeObj + timedelta(seconds=i) for i in range(nb_points)]
        #self.y_data = [0 for i in range(nb_points)]

        self.x_data = pd.to_datetime(x_data)
        start_time = self.x_data.iloc[0]
        # end_time = self.x_data.iloc[1]
        # difference = end_time - start_time
        # seconds = difference.total_seconds()
        # print(type(difference))
        self.x_data = [str(int((end_time - start_time).total_seconds()/60)) + ":" + str(int((end_time - start_time).total_seconds()%60)) + ":" + str(int(((end_time - start_time).total_seconds()%1)*1000)) for end_time in self.x_data]
        # self.x_data = [(end_time - start_time).total_seconds() for end_time in self.x_data]
        # print(x_data)
        # self.x_data = [str(int((end_time-start_time).total_seconds()*100)) for end_time in self.x_data]

        self.y_data = y_data

        # print(self.x_data)
        # Add horizonal lines at every high velocity point
        #self.ax.axvline(x=self.x_data[500], color='r', linestyle='-')

        # Create the plot

        self.reference_line = reference_line
        self.plot = self.ax.plot(self.x_data, self.y_data, label=label, color=color)[0]

        # self.plot = self.ax.plot(self.x_data, self.reference_line, label=label, color="red")[0]
        if(vertical_threshold>0):
            for i in range(len(self.x_data)-1):
                if(abs(self.y_data[i] - self.y_data[i+1]))>vertical_threshold:
                    y1 = min([self.y_data[i],self.y_data[i+1]]) - 10
                    y2 = max([self.y_data[i], self.y_data[i + 1]]) + 10
                    self.plot = self.ax.plot([self.x_data[i],self.x_data[i+1]], [y1,y2], label=label, color="red", linewidth=3)[0]

        # Set default axis limits
        #self.ax.set_ylim(0, 100)
        #self.ax.set_xlim(self.x_data[0], self.x_data[-1])
        
        # Label Axes
        self.ax.set_xlabel('Time (min:sec:msec)')
        self.ax.set_ylabel(f'{label} (Degrees)') 

        # Auto format date labels
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack()


class ScaleSlider(tk.Frame):
    def _init_(self, parent, length, plots):
        super()._init_(parent)

        self.plots = plots
        self.values = plots[0].x_data

        self.toIndex = len(self.values) - 1

        self.minIndex = 0
        self.maxIndex = 0

        # Labels
        self.minLabel = tk.Label(self, text="Min:")
        self.minLabel.grid(column=0, row=0)
        self.maxLabel = tk.Label(self, text="Max:")
        self.maxLabel.grid(column=0, row=1)

        # Sliders
        self.sliderMin = tk.Scale(self, from_=0, to=self.toIndex, length=length, orient='horizontal',
                                  command=self.minSliderChanged, showvalue=0, sliderlength=10, relief=tk.GROOVE)
        self.sliderMin.grid(column=1, row=0)

        self.sliderMax = tk.Scale(self, from_=0, to=self.toIndex, length=length, orient='horizontal',
                                  command=self.maxSliderChanged, showvalue=0, sliderlength=10, relief=tk.GROOVE)
        self.sliderMax.grid(column=1, row=1)
        self.sliderMax.set(self.toIndex)
        # Values
        self.minValueLabel = tk.Label(self, text=self.values[0])
        self.minValueLabel.grid(column=2, row=0)
        self.maxValueLabel = tk.Label(self, text=self.values[self.toIndex])
        self.maxValueLabel.grid(column=2, row=1)

    def minSliderChanged(self, minIndex):
        self.minIndex = int(minIndex)
        if (self.minIndex >= self.maxIndex - 1):
            self.minIndex = self.maxIndex - 1
            self.sliderMin.set(self.minIndex)

        self.minValueLabel.configure(text=f"{self.values[self.minIndex]}")
        self.updatePlots()

    def maxSliderChanged(self, maxIndex):
        self.maxIndex = int(maxIndex)
        if (self.maxIndex <= self.minIndex + 1):
            self.maxIndex = self.minIndex + 1
            self.sliderMax.set(self.maxIndex)

        self.maxValueLabel.configure(text=f"{self.values[self.maxIndex]}")
        self.updatePlots()

    def updatePlots(self):
        for plot in self.plots:
            # Update Plot Limits
            print(plot.ax)
            plot.ax.set_xlim(self.values[self.minIndex], self.values[self.maxIndex])
            maxYValue = max(plot.y_data[self.minIndex:self.maxIndex + 1])
            plot.ax.set_ylim(min(plot.y_data[self.minIndex:self.maxIndex + 1]) - maxYValue * 0.10, maxYValue * 1.10)
            plot.canvas.draw_idle()  # redraw plot


class GUI(tk.Tk):
    def __init__(self, analyzer, data, title, vertical_threshold, Window_name):
        super()._init_()

        self.analyzer = analyzer

        self.protocol("WM_DELETE_WINDOW", self.analyzer.close)

        
        # Root window configuration
        self.title(title)
        self.geometry('1200x750+200+10')
        self.row = 0

        # self.name = tk.Frame(self)
        # self.name.grid(row=0, column=0)
        self.name = tk.Label(self, text=Window_name)
        self.name.config(font=("Courier", 12))
        self.name.grid(row=0,column=0)
        # Pressure Figure
        yaw_reference = 0  # base line value for yaw
        self.yawPlot = Plot(self, data.loc[:,"time"], data.loc[:,"yaw"], "Yaw", "blue", [yaw_reference for i in range(len(data.loc[:,"time"]))], vertical_threshold)
        self.yawPlot.grid(row=1, column=0)
        pitch_reference = 0  # base line value for pitch
        self.pitchPlot = Plot(self, data.loc[:,"time"], data.loc[:,"pitch"], "Pitch", "green", [pitch_reference for i in range(len(data.loc[:,"time"]))], vertical_threshold)
        self.pitchPlot.grid(row=2, column=0)

        self.slider = ScaleSlider(self, length=600, plots=[self.yawPlot, self.pitchPlot])
        self.slider.grid(row=3, column=0)

        self.label = tk.Label(self, text="Try slowing down your yaw, it was too high at minuite 3:14")
        self.label.config(font =("Courier", 10))
        self.label.grid(row=4, column=0)



    def close(self):
        print("Closing Application")
        self.destroy()

class Analyzier():
    def _init_(self):
        self.dataFrame = None

    def openFile(self, filename):
        # This will open a given
        df = pd.read_csv(filename) # Reading the file
        #print(df.loc[:,"yaw"])
        self.dataFrame = df
        return df
    
    def analyze(self, data_type, dataFrame, title, vertical_threshold, Window_name):
        if(data_type!=0):
            self.dataFrame = dataFrame
        # This will do all the analysis programming and open an Tkinter Window (GUI)
        # self.openFile(filename)

        if False: # You can remove this when the analysis code is read to run
            data = self.dataFrame
            

            yawVelocityData = [] # This could be a pandas array
            #Pseudo Code
            for index in range(len(data)-1):
                point1 = data[index] # How to get row from pandas Array
                point2 = data[index+1]
                timePoint1 = point1.loc[:,"time"] # How to get item from row of padas array
                #yawPoint1 = #...
                #timePoint2 = #...
                #yawPoint2 = #...

                yawVelocity1To2 = yawPoint2-YawPoint1 / timePoint2-timePoint1 # May have to use datetime.timedelta()
                yawVelocityData.add({time: timePoint2, velocity: yawVelocity1To2 })

            # Here you'll have a yawVeloictyData array of velocities then do#array.count() > 15
            # you could plot velocities

            # Accelerations is the same process but going over velocity datas



            # If number of times velocity is over 15mm/s,, > 5 Intermediate , > 10 Noice , < 5 Expert

            # If numer of times acceleration is over 2mm/s^2,, > 5 Intermediate , > 10 Noice , < 5 Expert

        self.skill = "Expert" # Or whatever it is

        self.gui = GUI(self, self.dataFrame, title, vertical_threshold, Window_name)
        # Run GUI
        self.gui.mainloop()

    def close(self):
        # Close the tkinter window
        try:
            self.gui.close()
        except Exception:
            pass

    # Extras
    def compareWith(self, filename1, filename2):
        # Compare two datasets, see who did better
        pass

    def saveAnalysisAs(self, analysis):
        # Save 
        pass

    def displayExtraTips(self, tips):
        # Display tips on how the user can improve
        pass

    def displayKeyAreas(self, notes):
        # Inform the user of all places they perfomred less that Expertly ("Too high velocity at minute 1:45")
        pass

def calculate_velocity(df):
    x_data = df.loc[:,"time"]
    pitch_data = df.loc[:,"pitch"]
    yaw_data = df.loc[:,"yaw"]
    pitch_velocity = [0]
    yaw_velocity = [0]
    x_data = pd.to_datetime(x_data)

    for i in range(len(x_data)-1):
        time_difference = (x_data.iloc[i+1] - x_data.iloc[i]).total_seconds()
        pv = (pitch_data.iloc[i+1] - pitch_data.iloc[i]) / time_difference
        yv = (yaw_data.iloc[i+1] - yaw_data.iloc[i]) / time_difference
        pitch_velocity.append(pv)
        yaw_velocity.append(yv)


    df['pitch'] = pitch_velocity
    df['yaw'] = yaw_velocity

    return df

def calculate_acceleration(df):
    x_data = df.loc[:,"time"]
    pitch_data = df.loc[:,"pitch"]
    yaw_data = df.loc[:,"yaw"]
    pitch_acc = [0,0]
    yaw_acc = [0,0]
    x_data = pd.to_datetime(x_data)

    for i in range(1,len(x_data)-1):
        time_difference = (x_data.iloc[i+1] - x_data.iloc[i]).total_seconds()
        pa = (pitch_data.iloc[i+1] - pitch_data.iloc[i]) / time_difference
        ya = (yaw_data.iloc[i+1] - yaw_data.iloc[i]) / time_difference
        pitch_acc.append(pa)
        yaw_acc.append(ya)


    df['pitch'] = pitch_acc
    df['yaw'] = yaw_acc

    return df

if __name__ == "__main__":
    analyzer = Analyzier()
    df = analyzer.openFile("sampleData.csv")
    analyzer.analyze(0,None, "Movement", 8, "Movement Data")

    velocity_df = calculate_velocity(df)
    analyzer2 = Analyzier()
    analyzer2.analyze(1, velocity_df, "Movement Velocity", 0, "Velocity Data")

    acceleration_df = calculate_acceleration(velocity_df)
    analyzer2 = Analyzier()
    analyzer2.analyze(2, acceleration_df, "Movement Acceleration", 0, "Acceleration Data")
