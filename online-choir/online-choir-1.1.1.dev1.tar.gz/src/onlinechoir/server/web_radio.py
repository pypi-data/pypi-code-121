import audioop
from pathlib import Path

import numpy as np
import threading
from queue import Queue, Empty
from subprocess import Popen, PIPE

from ..common.log import parse_args_and_set_logger, logger
from ..common.audio_codecs import StereoDecoder


NOISE_AMPLITUDE = 100
STEREO_NOISE = audioop.tostereo(np.random.randint(low=-NOISE_AMPLITUDE, high=NOISE_AMPLITUDE,
                                                  size=512, dtype='i2').tobytes(), 2, 1, 1)
ICES2_PATH = '/usr/bin/ices2'


class WebRadio:
    def __init__(self, config_file: str):
        self._q = Queue()
        self._ices = Popen([ICES2_PATH, config_file], stdin=PIPE)
        self._broadcast_thread = threading.Thread(target=self._broadcaster, name='radio broadcaster')
        self._broadcast_thread.start()
        self._decoder = StereoDecoder()

    @classmethod
    def is_available(cls) -> bool:
        return Path(ICES2_PATH).exists()

    def add_data(self, data: bytes):
        idx = StereoDecoder.peek_frame_index(data)
        if idx < 0:
            return
        if idx == 0:
            self._decoder = StereoDecoder()  # reset decoder
        left, right = self._decoder.decode_left_right(data)
        self._q.put_nowait(audioop.add(audioop.tostereo(left, 2, 1, 0), audioop.tostereo(right, 2, 0, 1), 2))

    def _broadcaster(self):
        while True:
            try:
                data = self._q.get_nowait()
                if data is None:
                    break
            except Empty:
                data = STEREO_NOISE
            self._ices.stdin.write(data)
        logger.debug("broadcaster completed")

    def close(self):
        self._q.put_nowait(None)
        self._broadcast_thread.join()
        self._ices.kill()


def cli():
    import wave
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('fname')
    parsed_args = parse_args_and_set_logger(parser)

    assert WebRadio.is_available()
    radio = WebRadio('/Users/olivier/tmp/ices-2.0.3/ices.xml')
    input("Press Enter to continue...")
    with wave.open(parsed_args.fname, 'rb') as wf:
        while True:
            data = wf.readframes(512)
            if not data:
                break
            radio.add_data(data)
    input("Press Enter to continue...")
    radio.close()
    exit(0)
