import sacn
from helpers import RGBDevice, hsv_to_big_rgb
import constants
import colors
import time

receiver = sacn.sACNreceiver()
device = RGBDevice(constants.baudrate, constants.timeout, constants.port)


@receiver.listen_on('universe', universe=1)
def callback(packet):
    framebuffer = []
    color = []
    for i in packet.dmxData:
        if len(color) < 3:
            color.append(i)
        else:
            framebuffer.append(tuple(color))
            color = []
            color.append(i)
    print(framebuffer)
    device.send_frame(framebuffer)
    time.sleep(0.1)
    

receiver.start()