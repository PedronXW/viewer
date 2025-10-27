import cv2


def get_video_stream(source):
    cap = cv2.VideoCapture(source)
    return cap

def read_frame(cap):
    ret, frame = cap.read()
    if not ret:
        return None
    return frame
