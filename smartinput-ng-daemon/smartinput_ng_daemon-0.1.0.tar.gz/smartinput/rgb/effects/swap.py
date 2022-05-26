from smartinput.rgb.helpers import RGBDevice, hsv_to_big_rgb, fade
from smartinput.rgb import constants
from smartinput.rgb import colors
import time
from PIL import ImageColor


def swap(device: RGBDevice, options: dict):
    delay = (100 - options.get("speed")) / 1000 + 0.01
    original_color1 = ImageColor.getcolor(options['color1'], "RGB")[:3]
    original_color2 = ImageColor.getcolor(options['color2'], "RGB")[:3]

    while True:
        for i in range(0, 100):
            framebuffer = []

            if i > 50:
                incolor1, incolor2 = original_color1, original_color2
            else:
                incolor1, incolor2 = original_color2, original_color1

            color1 = fade(incolor1, incolor2, i / 100)
            color2 = fade(incolor2, incolor1, i / 100)

            framebuffer.append(color1)
            framebuffer.append(color2)
            framebuffer.append(color2)
            framebuffer.append(color1)

            device.send_frame(framebuffer)
            time.sleep(delay)
