import cv2 as cv
from hand_detector import HandDetector as hd

widthCam, heightCam = 650,480

cap = cv.VideoCapture(1)
cap.set(3,widthCam)
cap.set(4,heightCam)
pTime = 0

gesture_path = '/Users/elie080106/gestureControl/assets/gesture_recognizer.task'
detection = hd(gesture_path)

detection.run()

