from smartinput.rgb.helpers import RGBDevice, hsv_to_big_rgb
from smartinput.rgb import constants
import time


def breathe(device: RGBDevice, options: dict):
    delay = (100 - options.get("speed")) / 1000 + 0.01

    while True:
        for i in range(0, 6):
            hue = i / options["num_colors"]
            for k in [True, False]:
                for j in range(100):
                    v = j / 100 if k else 1 - j / 100
                    color = hsv_to_big_rgb(hue, 1, v)
                    framebuffer = [color]*4
                    device.send_frame(framebuffer)
                    time.sleep(delay)
