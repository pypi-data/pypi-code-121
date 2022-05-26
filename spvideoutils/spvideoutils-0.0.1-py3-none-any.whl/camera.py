"""Class to represent the camera device using open cv."""

import cv2


class Camera:
    """Manipulate the camera object. Use my current camera settings by default.

    :param port: Port index of the camera. Default to 1 since 0 is internal.
    :param width: Frame width setting in camera. Default to 1280.
    :param height: Frame height setting in camera. Default to 800.
    :param fps: Frame per second setting in camera. Default to 120.
    """

    def __init__(self, port=1, width=1280, height=800, fps=120):
        """Constructor method."""
        self.cap = cv2.VideoCapture(port)

        if not self.cap.isOpened():
            raise ValueError(f"Could not open camera at port={port}")

        self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)
        self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.cap.set(cv2.CAP_PROP_FPS, fps)

    def width(self):
        """Return the width of the frame in camera.

            :returns: Width in pixels.
            :rtype: int
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH))

    def height(self):
        """ Returns the height of the frame in camera.

            :returns: Height in pixels.
            :rtype: int
        """
        return int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def fps(self):
        """Return the frames per second of camera."""
        return int(self.cap.get(cv2.CAP_PROP_FPS))

    def read_frame(self):
        """Read a frame from the camera."""
        ret, frame = self.cap.read()
        if not ret:
            raise IOError("Camera could not capture a frame")
        return frame

    def read_gray_frame(self):
        """Return the gray frame from the camera."""
        frame = self.read_frame()
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return gray

    def take_video(self, fname, time_secs=4):
        """Capture video from camera to a file.

            :fname: Output filename with mp4 extension
            :time_secs: Time in seconds for recording.

            :returns: None
        """
        writer = cv2.VideoWriter(
            fname,
            cv2.VideoWriter_fourcc(*"mp4v"),
            self.fps(),
            (self.width(), self.height()),
        )

        num_frames = time_secs * self.fps()

        for _ in range(num_frames):
            frame = self.read_frame()
            writer.write(frame)

        writer.release()

    def take_picture(self, fname):
        """ Save a frame from the camera to a file.

            :fname: Output filename with .png extension.
            :returns: None
        """
        frame = self.read_frame()
        cv2.imwrite(fname, frame)

    def __del__(self):
        self.cap.release()
