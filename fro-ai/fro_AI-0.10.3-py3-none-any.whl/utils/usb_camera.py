from .camera import Camera
import atexit
import cv2
import traitlets


class USBCamera(Camera):

    capture_fps = traitlets.Integer(default_value=30)
    capture_width = traitlets.Integer(default_value=640)
    capture_height = traitlets.Integer(default_value=480)
    capture_device = traitlets.Integer(default_value=0)

    def __init__(self, *args, **kwargs):
        super(USBCamera, self).__init__(*args, **kwargs)
        try:
            self.cap = cv2.VideoCapture(self.capture_device)

            re, _ = self.cap.read()

            if not re:
                raise RuntimeError('Could not read image from camera.')

        except:
            raise RuntimeError(
                'Could not initialize camera.  Please see error trace.')

        atexit.register(self.cap.release)

    def _read(self):
        re, image = self.cap.read()
        if re:
            return image
        else:
            raise RuntimeError('Could not read image from camera')
