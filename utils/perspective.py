import cv2
import numpy as np

def correct_perspective(frame, pts_src, size=(128, 64)):
    pts_dst = np.array([[0,0],[size[0]-1,0],[size[0]-1,size[1]-1],[0,size[1]-1]], dtype='float32')
    M = cv2.getPerspectiveTransform(np.array(pts_src, dtype='float32'), pts_dst)
    return cv2.warpPerspective(frame, M, size)
