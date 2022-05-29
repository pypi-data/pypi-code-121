"""Utilities for simple tasks."""
import cv2

# font
font = cv2.FONT_HERSHEY_SIMPLEX
thickness = 2
font_scale = 1

def fprint(frame, msg):
    """Print msg on top of the frame.

    :param numpy.array frame: Frame to draw the message on.
    :param str msg: Text message to display
    :return: None
    """
    frame = cv2.putText(frame, msg, (10, 30), font,
                      font_scale, (255, 255, 0), thickness, cv2.LINE_AA)