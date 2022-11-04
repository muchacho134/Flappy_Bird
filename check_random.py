import random
import cv2 as cv
VID_CAP = cv.VideoCapture(0)
window_size = (VID_CAP.get(cv.CAP_PROP_FRAME_WIDTH), VID_CAP.get(cv.CAP_PROP_FRAME_HEIGHT)) 
print(window_size)
print(int((random.uniform(120 - 1000, window_size[1] - 120 - 250 - 1000))))