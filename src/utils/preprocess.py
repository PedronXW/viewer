import cv2
import numpy as np

def resize_frame(frame, width=640):
    h, w = frame.shape[:2]
    scale = width / w
    return cv2.resize(frame, (width, int(h*scale)))
