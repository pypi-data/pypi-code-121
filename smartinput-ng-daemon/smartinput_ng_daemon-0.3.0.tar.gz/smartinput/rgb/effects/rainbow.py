from smartinput.rgb.helpers import RGBDevice, hsv_to_big_rgb
from smartinput.rgb import constants
from smartinput.rgb import colors
import time

def rainbow(device: RGBDevice, options: dict):
    delay = (100 - options.get("speed")) / 1000 + 0.01
    shift_delta = options.get("speed") / 1000

    while True:
        shift = 0
        while shift < 1:
            framebuffer = []
            for pixel in range(constants.num_pixels):
                framebuffer.append(hsv_to_big_rgb(
                    pixel/constants.num_pixels + shift, 1, 1))
            device.send_frame(framebuffer)
            time.sleep(delay)
            shift += shift_delta

if __name__ == "__main__":
    device = RGBDevice(constants.baudrate, constants.timeout, constants.port)
    rainbow(device)
