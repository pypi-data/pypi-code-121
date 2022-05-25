from PIL import Image
import cv2
import numpy as np


class ToGrayScale(object):
    """
    This class is needed to transform rbg numpy frames to grayscale numpys during the training process with pytorch.
    """

    def __call__(self, frame):
        """
        Custom transformation class to convert given rgb frame to grayscale frame

        :param frame: [required] numpy frame with shape (BxHx3)
        :return: numpy frame with with shape (BxHx3)
        """

        frame = np.asarray(frame)
        # print(type(frame))
        # print(frame.shape)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        # gray = cv2.resize(gray,(224, 224))
        frame_gray = cv2.cvtColor(gray, cv2.COLOR_GRAY2RGB)
        # hist_cl1 = cv2.calcHist([cl1], [0], None, [256], [0, 256])

        frame_gray = Image.fromarray(frame_gray)
        return frame_gray

    def __repr__(self):
        return self.__class__.__name__ + 'convert2Grayscale'

