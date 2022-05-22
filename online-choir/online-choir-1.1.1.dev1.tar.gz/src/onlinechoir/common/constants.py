import numpy as np
from enum import IntEnum

SAMPLING_RATE = 44100
FRAME_SIZE = 512
BYTE_ENCODING = np.dtype('i2')
SATURATION_LEVEL = 0.999
CHUNKS_PER_SECOND = SAMPLING_RATE / FRAME_SIZE
CHUNKS_IN_FLIGHT = int(6 * CHUNKS_PER_SECOND)
SLAVE_PLAYBACK_BUFFER_SIZE = int(CHUNKS_PER_SECOND)
MASTER_PLAYBACK_BUFFER_SIZE = int(2 * CHUNKS_PER_SECOND)

KEEPALIVE_INTERVAL = 10
CONNECTION_TIMEOUT = 30


# TODO: replace idx = 0, -1 and -2 everywhere.
class FrameType(IntEnum):
    EOF = -1  # for lead track
    CHECK_IN = -1  # for slave client stream
    START = 0
    ABORT = -2
    KEEPALIVE = -3


VOCAL_GROUPS = ['No group', 'Soprano', 'Mezzo', 'Alto', 'Tenor', 'Baritone', 'Bass']
