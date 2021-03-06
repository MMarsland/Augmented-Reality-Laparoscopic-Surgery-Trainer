# Augmented Reality Laparoscopic Surgery Trainer
## Project Abstract
The field of laparoscopy is relatively new in the surgery world and it has distinct benefits over traditional “open” surgery techniques. However, these benefits come at the cost of a more complex procedure and a need for advanced training with the required equipment. In order to fulfill this need, various training aparati have been developed and tested, the most beneficial of which is Augmented Reality training modules as they combine the benefits of both physical simulators. Over the course of this project, we have developed a low-cost, stand-alone, training module instrumented with motion tracking sensors, Augmented Reality guidance and feedback, and a simple analysis system. This project can be easily carried into future years as the module built can easily continue to be improved through various methods and the research complete can be used to further branch this project into further territories. For the most part, this project has run smoothly over the two semesters, though this required some modifications and adjustments to the communication and team protocols as the project continued. We hope that the complete motion tracking and Augmented Reality training module will continue to be used in future projects for years to come and eventually be able to actively contribute to this vital field of advanced laparoscopic surgery training.


## Overview
This project involves the creation of an Augmented Reality Laparoscopic Surgery Training Apparatus. For a simple summary the final video for the Project is available on youtube:
https://www.youtube.com/watch?v=6su7bXyjUVA&t=7s&ab_channel=MichaelMarsland  

This project is broken up into a few parts: The collection of motion data from the sensors, the training program and real-time feedback, and the post-task analysis and evaluation.

The majority of the software for this project is written in python with some Arduino Code (C++) to interface with the sensors.

The hardware for the project is summarized in the final report but here is an image of the final set-up:
![alt text](images/apparatus-overview.jpg)



## Content
This github repo contains the main files for the project. Each item is described below:

### [augmented-reality](augmented-reality/)
The code for the python program that runs on the Jetson Nano. This includes the code for the
augmentedReality program that is displayed on the monitor as well as the code that collects data from the arduinos,
the analyzer code and the program code that ties it all together.

### [images](images/)
Some example images of the project and the projects various components

### [sensor-code](sensor-code/)
The code for the arduinos that collect data from the sensors and pass it along to the python program.

### [virtual-simulator](virtual-simulator/)
The code for the experimental tool-tip tracking virtual simulator built in blender. This is independent from the rest
of the project but may be useful for projects in future years.

### [Final Report]("Final Report - Group 33 - Augmented Reality Laparoscopic Surgery Trainer.pdf")
The final report for the project. This includes a more detailed overview of the project. I also includes the project
proposal and other important information about the project.

### [Nasr Paper]("Nasr et al - J Pediatric Surgery 2014.pdf")
A paper by Dr. Nasr et al that inspired the main work for this project.


### 3D Models
The 3D models for this project were created in OnShape. The files can be viewed here as well as copied to your own account if you wish to continue development.
https://cad.onshape.com/documents/7f866657db48ee6f939736f3/w/f6c8ad786f0bbfbba4a34716/e/9dcc6291ce942c2611d11cf7?renderMode=0&uiState=626053507ac13c055e536b5c

### Hardware
Data sheets and further information for the hardware components of this project (Jetson Nano, Arduino Uno, MPU6050, and VL53L0X) can be found on the internet. Links to some references follow but more information can be found through Google as required:
Jetson Nano - https://developer.nvidia.com/embedded/learn/get-started-jetson-nano-2gb-devkit
Arduino Uno - https://docs.arduino.cc/hardware/uno-rev3
MPU 6050 - https://invensense.tdk.com/wp-content/uploads/2015/02/MPU-6000-Datasheet1.pdf
VL53L0X - https://www.pololu.com/file/0J1187/vl53l0x.pdf

## How-to
In order to get the project running you must follow the procedure roughly outlined below. Some Modifications or additional steps may be required. Some hardware items were used that were not included in the project equipment, to exactly follow the steps below you will require an additional:
- HDMI Cable
- USB Mouse and Keyboard
- USB Splitter

1. Attach Jetson Nano to the Monitor via a usb cable (Cable not included in project equipment)
2. Attach USB camera into the Jetson Nano via USB port
3. Attach Mouse and Keyboard to the Jetson Nano via USB port (Mouse and keyboard not included)
4. Plug in included Jetson Nano Wifi Module via USB <br>
5. Ensure sensors are attched to the arduino. Follow the datasheet guides and port numbers as written in the sensor arduino code. In the final state of the project two arduino uno's were being used. It may or may  not be possible to connect all four sensors two one arduino simultaneously.
6. Plug in Arduino Uno (Or Arduino Uno's to the Jetson Nano via USB)
  1. At this point you will require a USB splitter (Not included in project equipment)
7. Plug in Jetson Nano with USB-C Power Cable
8. Log into Jetson Nano (Username: Laparo, Password: scopic)
9. Connect to the Arduino uno(s) through the Arduino IDE to find the corresponding COM numbers and ensure that the arduino has the correct code loaded on it (From the sensors-code) directory.
10. Clone this repo on the Jetson Nano and cd to the augmented-reality folder.
11. Modify program.py with the correct cameraID of the usb camera (Google how to find this as it sometimes changes), and with the corresponding COM(s) of the Arduino(s).
12. Run program.py in python3 and interact with the program via the mouse and keyboard on the attached monitor.
   
## Tips
 - The project is still in the development phases and many of the design decisions may still be modified and workshopped to find the best solution. Please take our work with a grain of salt and think critically if there is a better solution to a given problem.

## Contact
For questions, inquiries, and assistance please send an email to: michaelmarsland@cmail.carleton.ca

