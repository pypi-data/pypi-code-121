import asyncio
import numpy as np

from ..common.constants import SAMPLING_RATE, FRAME_SIZE
from ..common.log import logger

MAX_LATENCY = 120
MIN_CORRELATION = 100


def generate_test_audio():
    n = 264 * FRAME_SIZE
    freq_range = (50, 10000)
    freq = np.linspace(*freq_range, n)
    t = np.cumsum(freq) / 44100 * np.pi * 2
    sig = np.sin(t)
    return np.outer(sig, np.ones((2,)))


def calculate_latency(original, recoreded):
    c = np.correlate(recoreded, original)
    shift = np.argmax(np.abs(c))
    logger.debug(f"recorded var: {np.log10(recoreded.var())}dB, max correlation at {shift} with amplitude {c[shift]}")
    if abs(c[shift]) < 100:
        return None
    return shift / FRAME_SIZE


async def main(sig):
    import sounddevice
    assert len(sig) % FRAME_SIZE == 0
    to_play = np.concatenate((sig, np.zeros((MAX_LATENCY * FRAME_SIZE, 2))))
    res = np.empty((len(to_play),), dtype=np.float32)
    loop = asyncio.get_event_loop()
    end = asyncio.Event()

    class AudioIndex:
        idx: int = 0

    cur = AudioIndex()

    def callback(indata: np.ndarray, outdata: np.ndarray, frames: int, _, status: sounddevice.CallbackFlags):
        assert frames == FRAME_SIZE
        if status.output_underflow:
            print("Underflow")
            raise sounddevice.CallbackAbort
        assert status.input_underflow or not status
        res[cur.idx:cur.idx + len(indata)] = indata[:, 0]
        outdata[:, :] = to_play[cur.idx:cur.idx + FRAME_SIZE, :]
        cur.idx += FRAME_SIZE
        if cur.idx >= len(to_play):
            raise sounddevice.CallbackStop

    def finished_callback():
        loop.call_soon_threadsafe(end.set)

    stream = sounddevice.Stream(samplerate=SAMPLING_RATE,
                                blocksize=FRAME_SIZE,
                                channels=(1, 2),
                                dtype="float32",
                                callback=callback,
                                finished_callback=finished_callback)

    stream.start()
    await end.wait()
    stream.stop()
    stream.close()

    latency = calculate_latency(sig.mean(axis=1), res)

    print(f"Measured latency: {latency}")


def cli():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--input', default='assets/sound/sine.wav')
    parser.add_argument('-s', '--sine', action='store_true')
    parsed_args = parser.parse_args()

    if parsed_args.sine:
        sig = generate_test_audio()
    else:
        from ..common.audio_files import load_audio_file
        sig = load_audio_file(parsed_args.input).mean(axis=1)
    asyncio.run(main(sig))

    parser.exit(0)
