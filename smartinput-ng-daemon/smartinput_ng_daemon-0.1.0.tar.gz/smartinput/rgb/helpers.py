"""
Protocol:
Send numbers to the serial port. Send the rgb bytes in that order, then a control byte. Then start over

By default, the control byte is 0x00.
send a control byte of 0x01 after the very last value (blue of last pixel)

"""

from typing import Tuple, Optional
import serial
import colorsys


class RGBDevice:
    def __init__(self, baudrate=115200, timeout=0.1, port='/dev/ttyUSB0', serial_device: Optional[serial.Serial]=None) -> None:
        if serial_device:
            print("hi")
            self.device = serial_device
        else:
            self.device = serial.Serial(
                baudrate=baudrate, timeout=timeout, port=port)

    def send_frame(self, colors):
        for i, color in enumerate(colors):
            self.device.write(bytes(color))
            if i == len(colors) - 1:
                self.device.write(bytes([0x01]))
            else:
                self.device.write(bytes([0x00]))

        self.device.flush()


def hsv_to_big_rgb(h, s, v):
    """converts a hsv color with values from 0 to 1 to a rgb tuple with values from 0-255"""
    return tuple([int(i*255) for i in colorsys.hsv_to_rgb(h, s, v)])


def fade(a: Tuple[int], b: Tuple[int], progress: float):
    """generates the fade state from a to b at progress"""
    a_hsv = colorsys.rgb_to_hsv(a[0]/255, a[1]/255, a[2]/255)
    b_hsv = colorsys.rgb_to_hsv(b[0]/255, b[1]/255, b[2]/255)
    
    new_hsv = []

    for i in range(3):
      delta = b_hsv[i] - a_hsv[i]

      new_hsv.append(a_hsv[i] + delta * progress)
    
    return hsv_to_big_rgb(new_hsv[0], new_hsv[1], new_hsv[2])
