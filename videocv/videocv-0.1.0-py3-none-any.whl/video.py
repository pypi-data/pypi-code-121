import cv2


class Video:
    def __init__(self, video_file):
        self.cap = cv2.VideoCapture(video_file)

    def __call__(self):
        success, frame = self.cap.read()
        self.frame = frame

        key = cv2.waitKey(1) & 0xFF
        if key == 27:
            return False
        return success

    def __del__(self):
        self.cap.release()
