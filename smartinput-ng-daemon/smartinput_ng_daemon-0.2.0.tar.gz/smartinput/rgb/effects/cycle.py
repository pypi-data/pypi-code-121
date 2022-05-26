from smartinput.rgb.helpers import RGBDevice, hsv_to_big_rgb
from smartinput.rgb import constants
from smartinput.rgb import colors
import time


def cycle(device: RGBDevice, options: dict):
    delay = (100 - options.get("speed")) / 1000 + 0.01

    while True:
        for i in range(255):
            framebuffer = [hsv_to_big_rgb(i/255, 1, 1)]*constants.num_pixels
            device.send_frame(framebuffer)
            time.sleep(delay)


if __name__ == "__main__":
    device = RGBDevice(constants.baudrate, constants.timeout, constants.port)
    cycle(device)
