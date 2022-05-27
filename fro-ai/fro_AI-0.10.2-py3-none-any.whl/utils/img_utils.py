import cv2
import numpy as np
try:
    import jetson.utils
except:
    platform = 'not_jetson'
else:
    platform = 'jetson'


def roi(img, x1, x2, y1, y2):
    return img[x1:x2, y1:y2]


class RtpStream(object):
    def __init__(self,
                 remote_ip='192.168.55.100',
                 bitrate=4000000,
                 codec='h264',
                 remote_port=1234) -> None:
        super().__init__()

        self.remote_ip = remote_ip
        self.bitrate = bitrate
        self.codec = codec
        self.remote_port = remote_port

    def enable(self):
        if hasattr(self, 'rtp'):
            return
        if platform == 'jetson':
            self.rtp = jetson.utils.videoOutput(
                f"rtp://{self.remote_ip}:{self.remote_port}", [
                    "--headless",
                    f"--output-codec={self.codec}",
                    f"--bitrate={self.bitrate}",
                ])

    def disable(self):
        del self.rtp

    def put(self, bgr):
        if platform == 'jetson':
            if hasattr(self, 'rtp'):
                rgb = cv2.cvtColor(bgr, cv2.COLOR_BGR2RGB)
                cuda_mem = jetson.utils.cudaFromNumpy(rgb)
                self.rtp.Render(cuda_mem)


def bgr8_to_jpeg(value):
    return bytes(cv2.imencode('.jpg', value)[1])
