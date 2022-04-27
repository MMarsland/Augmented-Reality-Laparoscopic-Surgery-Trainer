'''This file contains the main code for the visuals of the program.

This includes all the openCV Screens that are shown including the program screens
and the augmented reality overlays.

@Author: Michael Marsland
@Date: April 2022
'''

class AR():
    '''This class runs the visuals for the program on the attached monitor.

    This includes not only the augmented reality but the main program itself.
    This is the main class for the project and could easily be split up into multiple
    classes for a cleaner workflow.

    The run() method of the AR class is the main loop of the program and continues to
    run until the program is terminated. The program transitions through the various
    states each having actions on state transtitions and different displays and/or
    augmentations depending on the current state.

    This class also contains many Augmented Reality and program helper methods some
    well founded and some more experimental.
    '''
    
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
