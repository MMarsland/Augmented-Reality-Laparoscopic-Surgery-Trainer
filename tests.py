# import the opencv library
import cv2
import numpy as np

# define a video capture object
vid = cv2.VideoCapture(0)

state = 0
colorState = 2
textState = 0
colorDetect = 0
quit = False
while(not quit):
    # Capture the video frame
    # by frame
    if (state == 0):
        ret, image = vid.read()
        #image = cv2.flip(image,1)

        #print(dims)
        height, width, other = image.shape
        scale = 500.0 / width

        image = cv2.resize(image, (0,0), fx=scale, fy=scale)
        h, w, other = image.shape
        overlayImg = image

        t = 100 # threshold for Canny Edge Detection algorithm
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured = cv2.medianBlur(grey, 15)

        # Create 2x2 grid for all previews
        grid = np.zeros([2*h, 2*w, 3], np.uint8)

        grid[0:h, 0:w] = image
        # We need to convert each of them to RGB from greyscaled 8 bit format
        grid[h:2*h, 0:w] = np.dstack([cv2.Canny(grey, t / 2, t)] * 3)
        grid[0:h, w:2*w] = np.dstack([blured] * 3)
        grid[h:2*h, w:2*w] = np.dstack([cv2.Canny(blured, t / 2, t)] * 3)

        edgesGrid = np.copy(grid[h:2*h, w:2*w])
        overlayImg[np.where((edgesGrid==[255,255,255]).all(axis=2))] = [0,0,255]

        # Display the resulting frame
        cv2.imshow('Video Feed', grid)
        #cv2.imshow('Edge Overlay', overlayImg)
    elif (state == 1):
        ret, image = vid.read()
        #image = cv2.flip(image, 1)

        height, width, other = image.shape
        #print(f"Height: ${height}, Width: ${width}")
        scale = 1000.0 / width
        image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        h, w, other = image.shape
        overlayImg = image

        t = 100  # threshold for Canny Edge Detection algorithm
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured = cv2.medianBlur(grey, 15)
        edgesGrid = np.dstack([cv2.Canny(blured, t / 2, t)] * 3)

        overlayImg[np.where((edgesGrid == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

        # Display the resulting frame
        # cv2.imshow('Video Feed', grid)
        cv2.imshow('Edge Overlay', overlayImg)
    elif (state == 2):
        # Color Detection
        ret, image = vid.read()
        image = cv2.flip(image, 1)
        height, width, other = image.shape
        image = cv2.resize(image, (1280, 800))
        h, w, other = image.shape

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


        #print(hsvRed)
        if (colorDetect == 1):
            lowerLimit = np.array(color_dict_HSV.get('black/')[1])
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

        # Display the resulting frame
        cv2.imshow('Color Detection', image)
    elif (state == 3):
        #print("In state 3")
        ret, image = vid.read()
        #print(image)
        image = cv2.flip(image, 1)

        height, width, other = image.shape
        #print(f"Height: ${height}, Width: ${width}")
        #scale = 1080.0 / width
        #image = cv2.resize(image, (1280, 800))
        h, w, other = image.shape
        #overlayImg = image

        # TODO: Ensure text is only re-calculated when it changes

        #bg_color = (0,0,255)
        font_face = cv2.FONT_HERSHEY_SIMPLEX
        scale = 0.8
        color = (0, 225, 75)
        if colorState == 1:
            color = (0, 165, 255)
        elif colorState == 2:
            color = (0, 0, 255)
        elif colorState == 3:
            color = (0, 0, 0)
        text = "SLOW DOWN"
        if textState == 1:
            text = "MAXIMUM ALLOWED SPEED EXCEEDED"
        elif textState == 2:
            text = "SPEED UP"
        elif textState == 3:
            text = "INCORRECT PLACEMENT"
        thickness = cv2.FILLED
        margin = 20

        txt_size = cv2.getTextSize(text, font_face, scale, thickness)

        start_x = width - txt_size[0][0] - margin
        start_y = height - margin
        pos = (start_x, start_y)
        #cv2.rectangle(image, pos, (end_x, end_y), bg_color, thickness)
        cv2.putText(image, text, pos, font_face, scale, color, 2, cv2.LINE_AA, False)
        # Display the resulting frame
        # cv2.imshow('Video Feed', grid)
        cv2.imshow('Text Overlay', image)
    elif (state == 4):
        # CIRCLE DETECTION
        ret, image = vid.read()
        #image = cv2.flip(image, 1)

        # print(dims)
        height, width, other = image.shape
        scale = 1000.0 / width

        image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        h, w, other = image.shape
        overlayImg = image

        t = 100  # threshold for Canny Edge Detection algorithm
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured = cv2.medianBlur(grey, 15)

        # Create 2x2 grid for all previews
        #grid = np.zeros([2 * h, 2 * w, 3], np.uint8)

        #grid[0:h, 0:w] = image
        # We need to convert each of them to RGB from greyscaled 8 bit format
        #grid[h:2 * h, 0:w] = np.dstack([cv2.Canny(grey, t / 2, t)] * 3)
        #grid[0:h, w:2 * w] = np.dstack([blured] * 3)
        #grid[h:2 * h, w:2 * w] = np.dstack([cv2.Canny(blured, t / 2, t)] * 3)

        #edgesGrid = np.copy(grid[h:2 * h, w:2 * w])
        #overlayImg[np.where((edgesGrid == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

        # Display the resulting frame
        #cv2.imshow('Video Feed', grid)
        # cv2.imshow('Edge Overlay', overlayImg)


        sc = 1  # Scale for the algorithm
        md = 30  # Minimum required distance between two circles
        # Accumulator threshold for circle detection. Smaller numbers are more
        # sensitive to false detections but make the detection more tolerant.
        at = 40
        circles = cv2.HoughCircles(blured, cv2.HOUGH_GRADIENT, sc, md, t, at)

        if circles is not None:
            #print(circles)
            if len(circles) == 1 and len(circles[0]) >= 1 and len(circles[0][0]) == 3:
                # We care only about the first circle found.
                circle = circles[0][0]
                x = int(circle[0])
                y = int(circle[1])
                radius = int(circle[2])

                #print(x, y, radius)

                # Highlight the circle
                cv2.circle(image, [x, y], radius, (0, 0, 255), -1)
                # Draw a dot in the center
                cv2.circle(image, [x, y], 1, (255, 0, 0), 1)

        cv2.imshow('Circle Detection', image)
    elif (state == 5):
        # LINE DETECTION
        ret, image = vid.read()
        image = cv2.flip(image, 1)

        # print(dims)
        height, width, other = image.shape
        scale = 1000.0 / width

        image = cv2.resize(image, (0, 0), fx=scale, fy=scale)
        #h, w, other = image.shape
        #overlayImg = image

        t = 100  # threshold for Canny Edge Detection algorithm
        grey = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blured = cv2.medianBlur(grey, 15)

        # Find Canny edges
        #canny = cv2.Canny(blured, t / 2, t)
        #contours, hierarchy = cv2.findContours(canny, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        #img = cv2.drawContours(image, contours, -1, (0, 255, 75), 2)

        #img_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        ret, im = cv2.threshold(grey, 100, 255, cv2.THRESH_BINARY_INV)
        contours, hierarchy = cv2.findContours(im, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        #for i in range(0, len(contours)):
        #    print(contours[i])
            #img = cv2.drawContours(image, contours, i, (0, 0, 255), 8)
        #    x, y = contours[i][0][0][0], contours[i][0][0][1]
        #    cv2.circle(image, [x, y], 25, (0, 0, 255), -1)
        #    cv2.imshow('Circle Detection', image)
        #    key = cv2.waitKey(1000) & 0xFF
        #    if key == ord('q'):
        #        quit = True
        #        break
        #    elif key == ord('r'):
        #        break
        color = (0, 225, 75)
        if colorState == 1:
            color = (0, 165, 255)
        elif colorState == 2:
            color = (0, 0, 255)
        elif colorState == 3:
            color = (0, 0, 0)
        img = cv2.drawContours(image, contours, -1, color, 8)

        # Create 2x2 grid for all previews
        # grid = np.zeros([2 * h, 2 * w, 3], np.uint8)

        # grid[0:h, 0:w] = image
        # We need to convert each of them to RGB from greyscaled 8 bit format
        # grid[h:2 * h, 0:w] = np.dstack([cv2.Canny(grey, t / 2, t)] * 3)
        # grid[0:h, w:2 * w] = np.dstack([blured] * 3)
        # grid[h:2 * h, w:2 * w] = np.dstack([cv2.Canny(blured, t / 2, t)] * 3)

        # edgesGrid = np.copy(grid[h:2 * h, w:2 * w])
        # overlayImg[np.where((edgesGrid == [255, 255, 255]).all(axis=2))] = [0, 0, 255]

        # Display the resulting frame
        # cv2.imshow('Video Feed', grid)
        # cv2.imshow('Edge Overlay', overlayImg)


        cv2.imshow('Circle Detection', img)

    # the 'q' button is set as the
    # quitting button you may use any
    # desired button of your choice
    key = cv2.waitKey(1) & 0xFF
    if key == ord('q'):
        break
    elif key == ord('a'):
        cv2.destroyAllWindows()
        state = (state + 1) % 5
    elif key == ord('c'):
        colorState = (colorState+1) % 4
    elif key == ord('s'):
        colorDetect = (colorDetect+1) % 2
    elif key == ord('t'):
        textState = (textState+1) % 4

# After the loop release the cap object
vid.release()
# Destroy all the windows
cv2.destroyAllWindows()
