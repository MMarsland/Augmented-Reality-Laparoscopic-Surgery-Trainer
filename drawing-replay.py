# import the opencv library
import cv2
import numpy as np
import time

# define a video capture object
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))

#Consants
STATE_STATES = 3
COLOR_STATES = 5
TEXT_STATES = 4
COLOR_DETECT_STATES = 2

DISPLAY_HEIGHT = 700
DISPLAY_WIDTH = 1200

#Global Variables
state = 2
colorState = 0
textState = 0
colorDetectState = 0

quit = False

color_dict_HSV = {'black': [[180, 255, 30], [0, 0, 0]],
              'white': [[180, 18, 255], [0, 0, 231]],
              'red1': [[180, 255, 255], [159, 50, 70]],
              'red2': [[9, 255, 255], [0, 50, 70]],
              'green': [[89, 255, 255], [36, 50, 70]],
              'blue': [[128, 255, 255], [90, 50, 70]],
              'yellow': [[35, 255, 255], [25, 50, 70]],
              'purple': [[158, 255, 255], [129, 50, 70]],
              'orange': [[24, 255, 255], [10, 50, 70]],
              'gray': [[180, 18, 230], [0, 0, 40]]}

# Line Drawing
points = []
frameCount = 0



# Test globals
frame_rate = 30
prevTime = 0
prev_frame_time = 0
new_frame_time = 0

framesBuffer = []
frameNumber = 0
inReplay = False
REPLAY_LENGTH_IN_FRAMES = 60

def addText(image, text, position):
    font_face = cv2.FONT_HERSHEY_SIMPLEX
    scale = 0.8
    thickness = 2
    margin = 20
    color = (0, 0, 255)

    txt_size = cv2.getTextSize(text, font_face, scale, thickness)
    start_x = DISPLAY_WIDTH - txt_size[0][0] - margin
    start_y = DISPLAY_HEIGHT - margin
    if (position == 1):
        start_y = start_y - txt_size[0][1] - margin
    pos = (int(start_x), int(start_y))
    #cv2.rectangle(image, pos, (end_x, end_y), bg_color, thickness)
    cv2.putText(image, text, pos, font_face, scale, color, thickness, cv2.LINE_AA, False)

while(not quit):
    try:
        if (state == 0):
            ret, image = vid.read()
            #image = cv2.flip(image, 1)
            #height, width, other = image.shape
            image = cv2.resize(image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            #h, w, other = image.shape

            #print(hsvRed)
            if (colorDetectState == 0):
                lowerLimit = np.array(color_dict_HSV.get('black')[1])
                upperLimit = np.array(color_dict_HSV.get('black')[0])

                hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            	# find the colors within the specified boundaries and apply
            	# the mask
                mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)
                color = (0, 225, 75)
                if colorState == 1:
                    color = (0, 165, 255)
                elif colorState == 2:
                    color = (0, 0, 255)
                elif colorState == 3:
                    color = (0, 0, 0)

                image[(mask==255)] = color

                coords = np.array(list(map(lambda x: x[0], cv2.findNonZero(mask))))

                #print(coords)
                text = "SELECT A CORNER"
                if (([0, 0] == coords).all(1).any()):
                    #print("TOP LEFT")
                    text = "TOP LEFT"
                if (([0, DISPLAY_HEIGHT-1] == coords).all(1).any()):
                    #print("BOTTOM LEFT")
                    text = "BOTTOM LEFT"
                if (([DISPLAY_WIDTH-1, 0] == coords).all(1).any()):
                    #print("TOP RIGHT")
                    text = "TOP RIGHT"
                if (([DISPLAY_WIDTH-1, DISPLAY_HEIGHT-1] == coords).all(1).any()):
                    #print("BOTTOM RIGHT")
                    text = "BOTTOM RIGHT"

                font_face = cv2.FONT_HERSHEY_SIMPLEX
                scale = 2
                thickness = 4
                margin = 20
                #color = (0, 225, 75)

                txt_size = cv2.getTextSize(text, font_face, scale, thickness)
                start_x = DISPLAY_WIDTH/2 - txt_size[0][0]/2 - margin
                start_y = DISPLAY_HEIGHT/2 - margin
                pos = (int(start_x), int(start_y))
                #cv2.rectangle(image, pos, (end_x, end_y), bg_color, thickness)
                cv2.putText(image, text, pos, font_face, scale, (0, 0, 255), 4, cv2.LINE_AA, False)

            # Display the resulting frame
            cv2.imshow('Corner Detection', image)
        elif (state == 1):
            time_elapsed = time.time() - prevTime
            ret, image = vid.read()

            #image = cv2.flip(image, 1)
            #height, width, other = image.shape
            image = cv2.resize(image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            if time_elapsed > 1./frame_rate:
                prevTime = time.time()
                # Actual FPS calc
                new_frame_time = time.time()
                fps = 1/(new_frame_time-prev_frame_time)
                prev_frame_time = new_frame_time
                fps = int(fps)
                fps = str(fps)

                framesBuffer.append(image);
                if len(framesBuffer) == REPLAY_LENGTH_IN_FRAMES:
                    framesBuffer.pop(0)

                if (inReplay):
                    image = framesBuffer[0]
                    addText(image, "REPLAY! FPS: "+fps, 1)
                    cv2.imshow('Frame Rate', image)
                    frameNumber += 1
                    if (frameNumber == REPLAY_LENGTH_IN_FRAMES):
                        inReplay = False

                else:
                    # Do something with your image here.
                    addText(image, "FPS: "+fps, 0)
                    cv2.imshow('Frame Rate', image)
        elif (state == 2):
            ret, image = vid.read()
            #image = cv2.flip(image, 1)
            image = cv2.resize(image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))
            lowerLimit = np.array(color_dict_HSV.get('black')[1])
            upperLimit = np.array(color_dict_HSV.get('black')[0])
            hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
            # find the colors within the specified boundaries and apply
            # the mask
            mask = cv2.inRange(hsv_image, lowerLimit, upperLimit)
            #color = (0, 225, 75)
            #if colorState == 1:
            #    color = (0, 165, 255)
            #elif colorState == 2:
            #    color = (0, 0, 255)
            #elif colorState == 3:
            #    color = (0, 0, 0)

            #image[(mask==255)] = color

            nonZero = cv2.findNonZero(mask)
            if nonZero is not None and len(nonZero) > 0:
                coords = np.array(list(map(lambda x: x[0], nonZero)))
                if len(coords > 0):
                    firstPoint = coords[0]
                    cv2.circle(image, [firstPoint[0], firstPoint[1]], 1, (0, 0, 255), 5)
                    # Pen location is x, y
                    frameCount += 1
                    if (frameCount == 5):
                        #print("POINT")
                        frameCount = 0
                        points.append((firstPoint[0], firstPoint[1]))

            if (len(points) > 1):
                contours = np.array(points)
                cv2.polylines(image, [contours], False, [0,0,255], 3)
            # Highlight the circle


            cv2.imshow('Contour Colouring', image)
            #cv2.line(image, [0,0], [DISPLAY_WIDTH-1,DISPLAY_HEIGHT-1], [0,0,255], 3)
            #contours = np.array([(375, 193), (364, 113), (277, 20), (271, 16), (52, 106), (133, 266), (289, 296), (372, 282)])
            #cv2.drawContours(image, [contours], -1, (0,0,255), 2)
            #cv2.polylines(image, contours, False, [255,0,255], 3)

            #cv2.imshow('Line Drawing', image)

    except Exception as e:
        #print(e)
        pass
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('a'):
        cv2.destroyAllWindows()
        state = (state + 1) % STATE_STATES
    elif key == ord('c'):
        colorState = (colorState+1) % COLOR_STATES
    elif key == ord('r'):
        inReplay = True
        frameNumber = 0
    elif key == ord('s'):
        colorDetectState = (colorDetectState+1) % COLOR_DETECT_STATES
        points = []
    elif key == ord('t'):
        textState = (textState+1) % TEXT_STATES


# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
