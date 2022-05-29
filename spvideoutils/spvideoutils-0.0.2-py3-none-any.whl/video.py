"""Wrapper over the video file."""

import cv2

class Splitter:
    """Splits a video file into frames."""

    def __init__(self, fname):
        """Construct a video object.
        :raises : Value error if the file is not found.
        """
        self.cap = cv2.VideoCapture(fname)
        if not self.cap.isOpened():
            raise ValueError(f"Could not open {fname}")

    def __iter__(self):
        return self

    def __next__(self):
        if self.cap.grab():
            flag, frame = self.cap.retrieve()
            if not flag:
                raise StopIteration
            else:
                return frame
        else:
            raise StopIteration

    def __del__(self):
        self.cap.release()

    def num_frames(self):
        """Return the number of frames in the video file."""
        return int(self.cap.get(cv2.CAP_PROP_FRAME_COUNT))

    def fps(self):
        """Return the fps of the video."""
        return int(self.cap.get(cv2.CAP_PROP_FPS))

    def width(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def height(self):
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))