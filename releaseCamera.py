import cv2
import numpy as np
import time

# define a video capture object
vid = cv2.VideoCapture(0)
vid.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter.fourcc('m','j','p','g'))

vid.release()
