# Tkinter
import tkinter as tk
# Matplotlib
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.ticker import MaxNLocator
# CSV Reader
import pandas as pd
import threading
import datetime

class Plot(tk.Frame):
    def __init__(self, parent, x_data, y_data, label, color, reference_line, vertical_threshold, fig_dimensions):
        super().__init__(parent)
        fig_width, fig_height, dpi = fig_dimensions
        # matplotlib figure
        self.figure = Figure(figsize=(fig_width, fig_height), dpi=dpi)
        self.ax = self.figure.add_subplot(111)
        self.ax.xaxis.set_major_locator(MaxNLocator(30))
        self.x_data = pd.to_datetime(x_data)
        start_time = self.x_data.iloc[0]
        self.x_data = [str(int((end_time - start_time).total_seconds()/60)) + ":" + str(int((end_time - start_time).total_seconds()%60)) + ":" + str(int(((end_time - start_time).total_seconds()%1)*1000)) for end_time in self.x_data]
        self.y_data = y_data

        # Create the plot
        self.reference_line = reference_line
        self.plot = self.ax.plot(self.x_data, self.y_data, label=label, color=color)[0]
        self.lines = []
        self.legendName = []
        self.lines.append(self.plot)
        self.legendName.append('Yaw')
        self.ax.legend(self.lines, self.legendName)

        # self.plot = self.ax.plot(self.x_data, self.reference_line, label=label, color="red")[0]
        if(vertical_threshold > 0):
            for i in range(len(x_data) - 1):
                if (abs(y_data[i] - y_data[i + 1])) > vertical_threshold:
                    y1 = min([self.y_data[i],self.y_data[i+1]]) - 10
                    y2 = max([self.y_data[i], self.y_data[i + 1]]) + 10
                    self.plot = self.ax.plot([self.x_data[i],self.x_data[i]], [y1,y2], label=label, color="red", linewidth=3)[0]

        # Label Axes
        self.ax.set_xlabel('Time (min:sec:msec)')
        self.ax.set_ylabel(label, fontsize=15)

        # Auto format date labels
        self.figure.autofmt_xdate()
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack()

    def addline(self, x_data, y_data, label, color, reference_line, vertical_threshold):

        x_data = pd.to_datetime(x_data)
        start_time = x_data.iloc[0]
        # end_time = self.x_data.iloc[1]
        # difference = end_time - start_time
        # seconds = difference.total_seconds()
        # print(type(difference))
        x_data = [str(int((end_time - start_time).total_seconds() / 60)) + ":" + str(
            int((end_time - start_time).total_seconds() % 60)) + ":" + str(
            int(((end_time - start_time).total_seconds() % 1) * 1000)) for end_time in x_data]
        # self.x_data = [(end_time - start_time).total_seconds() for end_time in self.x_data]
        # print(x_data)
        # self.x_data = [str(int((end_time-start_time).total_seconds()*100)) for end_time in self.x_data]


        # print(self.x_data)
        # Add horizonal lines at every high velocity point
        # self.ax.axvline(x=self.x_data[500], color='r', linestyle='-')

        # Create the plot

        reference_line = reference_line
        plot = self.ax.plot(x_data, y_data, label=label, color=color)[0]

        # self.plot = self.ax.plot(self.x_data, self.reference_line, label=label, color="red")[0]
        self.lines.append(plot)
        self.legendName.append('Pitch')
        self.ax.legend(self.lines, self.legendName)
        if (vertical_threshold > 0):
            for i in range(len(x_data) - 1):
                if (abs(y_data[i] - y_data[i + 1])) > vertical_threshold:
                    y1 = min([y_data[i], y_data[i + 1]]) - 10
                    y2 = max([y_data[i], y_data[i + 1]]) + 10
                    plot = self.ax.plot([self.x_data[i], self.x_data[i]], [y1, y2], label=label, color="red", linewidth=3)[0]
        return y_data
class ScaleSlider(tk.Frame):
    def __init__(self, parent, length, plots):
        super().__init__(parent)

        self.plots = plots
        self.values = plots[0][0].x_data

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
            minYValue = min(plot[0].y_data[self.minIndex:self.maxIndex + 1])
            maxYValue = max(plot[0].y_data[self.minIndex:self.maxIndex + 1])
            plot[0].ax.set_xlim(self.values[self.minIndex], self.values[self.maxIndex])
            plot[0].ax.set_ylim(minYValue - maxYValue * 0.10, maxYValue * 1.10)
            plot[0].canvas.draw_idle()  # redraw plot
            if(len(plot) > 1):
                for y_data in plot[1:]:
                    maxYValue = max(max(y_data[self.minIndex:self.maxIndex + 1]),maxYValue)
                    minYValue = min(min(y_data[self.minIndex:self.maxIndex + 1]), minYValue)
                    plot[0].ax.set_xlim(self.values[self.minIndex], self.values[self.maxIndex])
                    plot[0].ax.set_ylim(minYValue - maxYValue * 0.10, maxYValue * 1.10)
                    plot[0].canvas.draw_idle()  # redraw plot
class GUI(tk.Tk):
    def __init__(self, analyzer, data, Window_name, vertical_threshold, Window_title, graph_ylabel, fig_dimension):
        super().__init__()
        self.plots = []
        self.analyzer = analyzer
        self.protocol("WM_DELETE_WINDOW", self.close)
        # Root window configuration
        self.title(Window_name)
        self.geometry('1200x750+200+10')
        self.row = 0

        self.name = tk.Label(self, text=Window_title)
        self.name.config(font=("Courier", 12))
        self.name.grid(row=0,column=0)
        # Pressure Figure
        yaw_reference = 0  # base line value for yaw
        pitch_reference = 0  # base line value for pitch
        self.yawPlot = Plot(self, data.loc[:,"time"], data.loc[:,"yaw"], graph_ylabel, "blue", [yaw_reference for i in range(len(data.loc[:,"time"]))], vertical_threshold, fig_dimension)
        pitchdata = self.yawPlot.addline(data.loc[:,"time"], data.loc[:,"pitch"], "Pitch", "green", [pitch_reference for i in range(len(data.loc[:,"time"]))], vertical_threshold)
        self.yawPlot.grid(row=1, column=0)

        self.plots.append([self.yawPlot, pitchdata])
        self.label = tk.Label(self, text="Try slowing down your yaw, it was too high at minute 3:14")
        self.label.config(font =("Courier", 10))
        self.label.grid(row=4, column=0)

    def add_slider(self):
        self.slider = ScaleSlider(self, length=600, plots=self.plots)
        self.slider.grid(row=3, column=0)

    def add_graph(self, data, vertical_threshold, graph_ylabel, fig_dimension, hori_thresh=0):
        yaw_reference = 0  # base line value for yaw
        pitch_reference = 0  # base line value for pitch
        yawPlot = Plot(self, data.loc[:, "time"], data.loc[:, "yaw"], graph_ylabel, "blue",
                            [yaw_reference for i in range(len(data.loc[:, "time"]))], vertical_threshold, fig_dimension)
        pitchdata = yawPlot.addline(data.loc[:, "time"], data.loc[:, "pitch"], "Pitch", "green",
                                         [pitch_reference for i in range(len(data.loc[:, "time"]))], vertical_threshold)

        yawPlot.grid(row=2, column=0)

        if hori_thresh > 0:
            plot = yawPlot.ax.plot([yawPlot.x_data[0], yawPlot.x_data[-1]], [hori_thresh, hori_thresh], color="red", linewidth=3)[0]
            plot = yawPlot.ax.plot([yawPlot.x_data[0], yawPlot.x_data[-1]], [-hori_thresh, -hori_thresh], color="red", linewidth=3)[0]
        self.plots.append([yawPlot, pitchdata])
    def close(self):
        print("Closing Application")
        self.destroy()


class Analyzer():
    def __init__(self):
        self.dataFrame = None
        self.velocity_dataFrame = None
        self.acceleration_dataFrame = None

    def openFile(self, filename):
        # This will open a given
        df = pd.read_csv(filename) # Reading the file
        #print(df.loc[:,"yaw"])

        # Convert ms time into datetime
        fulldate = datetime.datetime.now()
        #print(df.loc[:, "time"])
        df.loc[:, "time"] = df.loc[:, "time"].apply(lambda time : fulldate + datetime.timedelta(milliseconds=time))
        #print(df.loc[:, "time"])
        self.dataFrame = df

    def calculate_velocity(self):
        df = self.dataFrame.copy(deep=True)
        x_data = df.loc[:, "time"]
        pitch_data = df.loc[:, "pitch"]
        yaw_data = df.loc[:, "yaw"]
        pitch_velocity = [0]
        yaw_velocity = [0]
        x_data = pd.to_datetime(x_data)

        for i in range(len(x_data) - 1):
            time_difference = (x_data.iloc[i + 1] - x_data.iloc[i]).total_seconds()
            pv = (pitch_data.iloc[i + 1] - pitch_data.iloc[i]) / time_difference
            yv = (yaw_data.iloc[i + 1] - yaw_data.iloc[i]) / time_difference
            pitch_velocity.append(pv)
            yaw_velocity.append(yv)

        df['pitch'] = pitch_velocity
        df['yaw'] = yaw_velocity

        self.velocity_dataFrame = df

    def calculate_acceleration(self):
        df = self.velocity_dataFrame.copy(deep=True)
        x_data = df.loc[:, "time"]
        pitch_data = df.loc[:, "pitch"]
        yaw_data = df.loc[:, "yaw"]
        pitch_acc = [0, 0]
        yaw_acc = [0, 0]
        x_data = pd.to_datetime(x_data)

        for i in range(1, len(x_data) - 1):
            time_difference = (x_data.iloc[i + 1] - x_data.iloc[i]).total_seconds()
            pa = (pitch_data.iloc[i + 1] - pitch_data.iloc[i]) / time_difference
            ya = (yaw_data.iloc[i + 1] - yaw_data.iloc[i]) / time_difference
            pitch_acc.append(pa)
            yaw_acc.append(ya)

        df['pitch'] = pitch_acc
        df['yaw'] = yaw_acc

        self.acceleration_dataFrame = df

    def analyze(self,filename):
        self.openFile(filename)
        self.calculate_velocity()
        self.calculate_acceleration()

        self.draw_position_graph("Position", 1.5, "Position Data", [18,8,65])
        self.draw_VelAcc_graph("Velocity and Acceleration", 8, 0, "Velocity and Acceleration Data", [22,5,55])



    def draw_position_graph(self, title, vertical_threshold, Window_name, fig_dimension):
        self.gui = GUI(self, self.dataFrame, title, vertical_threshold, Window_name, "Degrees", fig_dimension)
        self.gui.add_slider()
        # Run GUI
        # self.gui.mainloop()

    def draw_VelAcc_graph(self, title, vertical_threshold_vel, vertical_threshold_Acc, Window_name, fig_dimension):
        self.gui = GUI(self, self.velocity_dataFrame, title, vertical_threshold_vel, Window_name, "Velocity(Degrees/s)", fig_dimension)
        self.gui.add_graph(self.acceleration_dataFrame, vertical_threshold_Acc, "Acceleration(Degrees/s^2)", fig_dimension, hori_thresh=100)
        self.gui.add_slider()
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

if __name__ == "__main__":
    analyzer = Analyzer()
    analyzer.analyze("dataFiles/data-right-2022-03-23_16-02-16")
    #analyzer.analyze("data-right-2022-03-23_16-02-16")
    # t1 = threading.Thread(target=analyzer.draw_position_graph, args=("Position", 8, "Position Data", [22,8,65]))
    # t1.start()
    # t2 = threading.Thread(target=analyzer.draw_VelAcc_graph, args=("Velocity and Acceleration", 0, "Velocity and Acceleration Data", [26,5,55]))
    # t2.start()