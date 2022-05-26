from smartinput.rgb.helpers import RGBDevice
from smartinput.rgb import constants
import time
import colorsys
from PIL import ImageColor


def static(device: RGBDevice, options: dict):
    while True:
        color = ImageColor.getcolor(options['color'], "RGB")[:3]
        device.send_frame([color]*constants.num_pixels)
        time.sleep(10)
