"""
The client for the choir director.
"""
import asyncio
import numpy as np
import queue
try:
    import sounddevice
except (OSError, ModuleNotFoundError):
    pass
from functools import partial
from threading import Event, Lock
from typing import Optional, List

from ..common.utils import my_assert, iterate_queue
from ..common.log import logger
from ..common.audio_codecs import AudioDecoder, StereoEncoder
from ..common.constants import SAMPLING_RATE, FRAME_SIZE, CHUNKS_IN_FLIGHT, MASTER_PLAYBACK_BUFFER_SIZE, FrameType
from ..common.version import VERSION
from ..common.auth import AuthenticationHeader
from ..common.message_board import MessageBoard
from ..common.network import set_socket_settings


def prepare_queue(sig: np.ndarray, skip_seconds: Optional[float] = None) -> asyncio.Queue:
    n_frames, n_channels = sig.shape
    my_assert(n_channels == 2, "Stereo signal required")
    my_assert(n_frames % FRAME_SIZE == 0, "Signal must be adjusted to the chunk size")
    start_frame = int(round(skip_seconds * 44100 / FRAME_SIZE) * FRAME_SIZE) if skip_seconds else 0
    q = asyncio.Queue()
    for i in range(start_frame, n_frames, FRAME_SIZE):
        q.put_nowait(sig[i:i + FRAME_SIZE, :])
    q.put_nowait(None)
    return q


class MasterClient:
    def __init__(self, *,
                 mute: bool,
                 monitor_level: float,
                 gui_board: Optional[MessageBoard] = None,
                 in_device: Optional[int] = None, out_device: Optional[int] = None):
        logger.debug(f"Init master client with mute = {mute}, monitor_level = {monitor_level}, "
                     f"in_device = {in_device}, out_device={out_device}")
        my_assert(0 <= monitor_level <= 1, "Monitor level should be in [0, 1]")
        self.loop = None
        self.in_device = in_device
        self.out_device = out_device
        self.audio_in: List[np.ndarray] = []
        self.mute = mute
        self.monitor_mutex = Lock()
        self.monitor_level = monitor_level
        self.gui_board = gui_board

        # Playing status
        self.new_frame_received = None  # to be filled from main()
        self.encoder = StereoEncoder()
        self.stop_flag = False
        self.audio_mix: Optional[asyncio.Queue] = None  # to be filled from main()

    async def send_file(self, tcp_conn: asyncio.StreamWriter, data: asyncio.Queue):
        async for chunk in iterate_queue(data):
            while len(self.audio_in) < self.encoder.next_index - CHUNKS_IN_FLIGHT and not self.stop_flag:
                await self.new_frame_received.wait()
                self.new_frame_received.clear()
            if self.stop_flag:
                break
            tcp_conn.write(self.encoder(chunk))
            self.audio_mix.put_nowait(chunk.mean(axis=1))
            await tcp_conn.drain()

        tcp_conn.write(StereoEncoder.silence_frame(FrameType.EOF))
        await tcp_conn.drain()
        logger.info("Done sending file")

    async def play_stream(self, tcp_conn: asyncio.StreamReader):
        player_queue = queue.Queue()
        loop = asyncio.get_event_loop()
        playback_ended = asyncio.Event()
        decoder = AudioDecoder()
        paused = Event()
        paused.set()  # start the stream in pause mode
        playback_ended.set()  # set playback_ended, in case the session is aborted and the player never starts

        def player_callback(outdata: np.ndarray, frames: int, _, status):
            assert frames == FRAME_SIZE
            if status:
                logger.error(f"Audio callback error {status}")
            if paused.is_set():  # if not playing, play silence
                outdata[:, 0] = 0
            else:
                try:
                    chunk = player_queue.get_nowait()
                except queue.Empty:
                    logger.warning("Queue ran empty. Re-buffering")
                    paused.set()
                    outdata[:, 0] = 0
                    return
                if chunk is None:
                    raise sounddevice.CallbackStop
                with self.monitor_mutex:
                    monitor_level = self.monitor_level
                mon_chunk = self.audio_mix.get_nowait()
                outdata[:, 0] = self.audio_in[chunk] + monitor_level * mon_chunk
                self._update_gui('tick', chunk * FRAME_SIZE)

        def finished_callback():
            if loop.is_running():
                loop.call_soon_threadsafe(playback_ended.set)

        if not self.mute:
            stream = sounddevice.OutputStream(samplerate=SAMPLING_RATE, blocksize=FRAME_SIZE, channels=1,
                                              dtype="float32", callback=player_callback,
                                              finished_callback=finished_callback,
                                              device=self.out_device)
            stream.start()
        while len(self.audio_in) < max(1, self.encoder.next_index):
            try:
                data = await tcp_conn.readexactly(decoder.PACKET_SIZE)
            except asyncio.IncompleteReadError:
                data = None
            if not data:
                logger.info("Connection closed")
                break
            idx = decoder.peek_frame_index(data)
            if idx <= 0:
                logger.debug(f"Got frame {idx}")
                if idx == 0:
                    self._update_gui('session_active', True)
            if idx == -2:  # early drop message
                logger.debug("got early drop")
                break
            chunk = np.empty((FRAME_SIZE,))
            decoder(data, chunk)
            player_queue.put(len(self.audio_in))
            self.audio_in.append(chunk)
            self.new_frame_received.set()
            if not self.mute and paused.is_set() and player_queue.qsize() >= MASTER_PLAYBACK_BUFFER_SIZE:
                logger.info("Start playing after buffer reached sufficient level")
                playback_ended.clear()
                paused.clear()
        logger.info(f"Received {len(self.audio_in)} chunks (encoder at {self.encoder.next_index})")
        self._update_gui('session_active', False)
        if not self.mute:
            if paused.is_set() and not player_queue.empty():
                logger.info("Start playing after all chunks are received")
                playback_ended.clear()
                paused.clear()
            player_queue.put(None)
            logger.info("Waiting for audio to finish playing")
            await playback_ended.wait()
            stream.close()

    async def main(self, server_address: str, server_port: int, signal: Optional[asyncio.Queue]):
        msg = "live" if signal is None else f"{signal.qsize()} chunks"
        logger.info(f"Start client v{VERSION}, playing {msg}")
        self.loop = asyncio.get_event_loop()
        self.new_frame_received = asyncio.Event()
        logger.debug(f"Connecting to {server_address} port {server_port}")
        reader, writer = await asyncio.open_connection(server_address, server_port)
        set_socket_settings(writer)
        writer.write(AuthenticationHeader().to_bytes())
        await writer.drain()
        if signal is None:
            n_chan = min(2, sounddevice.query_devices(self.in_device, kind='input')['max_input_channels'])
            self.mute = True  # force mute mode to avoid audio
            signal = asyncio.Queue()
            stream_ended = asyncio.Event()
            frame_count = 0

            def rec_callback(indata: np.ndarray, frames: int, _, status):
                nonlocal frame_count
                chunk = np.empty((FRAME_SIZE, 2))
                sig = indata.mean(axis=1)
                chunk[:, 0] = sig
                chunk[:, 1] = sig
                self.loop.call_soon_threadsafe(partial(signal.put_nowait, chunk))
                self._update_gui('tick', frame_count)
                frame_count += frames

            def end_callback():
                self.loop.call_soon_threadsafe(stream_ended.set)

            stream = sounddevice.InputStream(SAMPLING_RATE, FRAME_SIZE, channels=n_chan, dtype='float32',
                                             latency='high', device=self.in_device, callback=rec_callback,
                                             finished_callback=end_callback)
            stream.start()
        else:
            stream = None
        self.audio_mix = asyncio.Queue()
        sender_task = asyncio.create_task(self.send_file(writer, signal))
        await self.play_stream(reader)
        if stream:
            stream.stop()
            await stream_ended.wait()
            stream.close()
        sender_task.cancel()
        writer.close()

    def _stop(self):
        """Stop the session immediately and return"""
        logger.info("Stopping the session")
        self.stop_flag = True
        self.new_frame_received.set()

    def stop(self):
        self.loop.call_soon_threadsafe(self._stop)

    def set_monitor_level(self, level: float):
        my_assert(0 <= level <= 1, f"Invalid level {level}")
        with self.monitor_mutex:
            self.monitor_level = level

    def get_recording(self) -> Optional[np.ndarray]:
        if not self.audio_in:
            return None
        res = np.empty((len(self.audio_in) * FRAME_SIZE,))
        for i, chunk in enumerate(self.audio_in):
            res[i * FRAME_SIZE:(i + 1) * FRAME_SIZE] = chunk
        return res

    def _update_gui(self, topic: str, msg):
        if self.gui_board is not None:
            self.gui_board.post_message(topic, msg)


def main(*, inpt: Optional[str], server: str, port: int, output: Optional[str], mute: bool, live: bool,
         monitor_level: float, skip_seconds: Optional[float]):
    import signal

    if inpt is None and not live:
        print("Must either provide an input file or choose the live option")
        exit(1)

    client = MasterClient(mute=mute, monitor_level=monitor_level)

    async def run_client():
        loop = asyncio.get_event_loop()
        try:
            loop.add_signal_handler(signal.SIGINT, client._stop)
        except NotImplementedError:
            pass
        if live:
            q = None
        else:
            from onlinechoir.common.audio_files import load_audio_file
            q = prepare_queue(load_audio_file(inpt), skip_seconds)
        await client.main(server, port, q)
        return

    asyncio.run(run_client())

    if output is not None:
        res = client.get_recording()
        if res is not None:
            import soundfile
            soundfile.write(output, res, SAMPLING_RATE)
    exit(0)
