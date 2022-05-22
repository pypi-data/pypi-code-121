"""
The client program to be used by signers.
"""

import asyncio
import numpy as np
from io import StringIO
from typing import Optional, MutableMapping, Any

from .db_calculator import DbCalculator
from ..common.audio_codecs import StereoDecoder, AdpcmEncoder
from ..common.audio_devices import check_audio_config
from ..common.constants import FRAME_SIZE, FrameType, KEEPALIVE_INTERVAL, CONNECTION_TIMEOUT
from ..common.version import VERSION
from ..common.auth import AuthenticationHeader
from ..common.log import logger
from ..common.network import set_socket_settings
from ..common.utils import iterate_queue, iterate_stream, my_assert, to_gain
from .gui_enums import GuiEvent, GuiState
from .sound_card import AudioIOStream


# Pipe structure:
# * TCP in: frames 0:n, ended by empty frame -1
# * TCP out: frames 0:n, started with -1, possibly ended by -2 (if ended early)


class SlaveClient:
    def __init__(self, in_config: MutableMapping[str, Any], gui, skip_check=False):
        self._config = in_config
        self._gui = gui
        self._state = None
        self._state_changed = None
        self._audio = None
        self._events = None
        self._reader: Optional[asyncio.StreamReader] = None
        self._writer: Optional[asyncio.StreamWriter] = None
        self._receive_task = None

        if not skip_check:
            check_audio_config(self._config, 'audio_input', 'audio_output')

        self._latency = int(in_config['latency'])

    def _change_state(self, state: GuiState, message: Optional[str] = None):
        self._state = state
        if self._gui:
            self._gui.change_state(state.value, message)
        self._state_changed.set()

    async def _receive_audio(self):
        # Keep decoding input TCP, queue it only if in the right state.
        # Keeps account of sections.
        # Adds the silence frames needed to compensate for latency.
        decoder: Optional[StereoDecoder] = None

        def start_session():
            nonlocal decoder
            logger.debug("Init decoder, flush audio queue and join session")
            self._events.put_nowait(GuiEvent.SESSION_STARTS.value)
            decoder = StereoDecoder()
            self._audio.flush_input()

        try:
            async for data in iterate_stream(self._reader, StereoDecoder.PACKET_SIZE, timeout=CONNECTION_TIMEOUT):
                idx = StereoDecoder.peek_frame_index(data)
                if idx == FrameType.KEEPALIVE:
                    logger.debug("got keep-alive message form server")
                    continue
                if idx == FrameType.START:
                    logger.debug("Session starting")
                    my_assert(decoder is None, "idx = 0 while decoder exists")
                    if self._latency == 0:
                        logger.warning("Session started, but client is not calibrated. Skipping.")
                        continue
                    if self._state == GuiState.READY:
                        start_session()
                    elif self._state == GuiState.SETTINGS and self._gui is not None:
                        logger.debug("settings still open, trying to close them")
                        self._state_changed.clear()
                        if self._gui.close_settings():
                            await self._state_changed.wait()
                            my_assert(self._state == GuiState.READY, "State should be READY here")
                            start_session()
                        else:
                            logger.warning("Session starting but settings can not be closed")
                    else:
                        logger.error(f"Session starting but state is {self._state}")
                if decoder is not None:
                    if self._state not in (GuiState.READY, GuiState.PLAYING):
                        logger.warning("State changed during session. Interrupting")
                        decoder = None
                        continue
                    if idx >= 0:
                        sig = np.empty((FRAME_SIZE, 2), dtype=np.float32)
                        decoder(data, sig)
                        self._audio.add_input_chunk(idx, sig)
                    else:
                        my_assert(idx == FrameType.EOF, f"Expected audio frame or EOF, but got {idx}")
                        logger.debug("Session ending")
                        # add silence to compensate for latency
                        silence = np.zeros((FRAME_SIZE, 2), dtype=np.float32)
                        next_idx = decoder.next_index
                        for i in range(next_idx, next_idx + self._latency):
                            self._audio.add_input_chunk(i, silence)
                        self._audio.add_end_marker()
                        decoder = None
        except asyncio.TimeoutError:
            logger.warning("Server not responding")
        except ConnectionResetError:
            logger.warning("Connection got reset")
        except asyncio.CancelledError:
            logger.info("Receiver cancelled")
        else:
            logger.info("Server closed connection")
        if decoder:  # stop playing if connection is lost
            logger.warning("Add end marker since server closed during session")
            self._audio.add_end_marker()

    async def _record_session(self):
        my_assert(self._state == GuiState.READY, "start playing while state is not ready")
        self._change_state(GuiState.PLAYING)
        self._writer.write(AdpcmEncoder.silence_frame(FrameType.CHECK_IN))
        await self._writer.drain()
        await self._audio.buffer_ready()
        logger.info("Sing!")
        latency_drop_count = self._latency
        db_calculator = DbCalculator(gain_db=self._config.get('gain', 0))
        encoder = AdpcmEncoder()
        failed = False
        async for idx, chunk in self._audio.play_and_record(self._config.get('audio_input', ''),
                                                            self._config.get('audio_output', ''),
                                                            KEEPALIVE_INTERVAL):
            if idx == FrameType.ABORT:
                logger.warning("Session failed. Dropping")
                data = AdpcmEncoder.silence_frame(FrameType.ABORT)
                failed = True
                if self._gui is not None:
                    self._gui.set_signal_level(None)
            elif idx == FrameType.KEEPALIVE:
                data = AdpcmEncoder.silence_frame(FrameType.KEEPALIVE)
            else:
                my_assert(not failed, "Audio came after the drop frame")
                # report on signal level if the system is not lagging
                if self._gui is not None and self._audio.backlog_size() == 0:
                    db = db_calculator.from_sample(chunk)
                    self._gui.set_signal_level(db)
                if latency_drop_count:
                    latency_drop_count -= 1
                    continue
                else:
                    my_assert(idx == encoder.next_index + self._latency, "inconsistent chunks")
                    data = encoder((db_calculator.gain * (1 if self._gui is None else self._gui.mute.get())) * chunk)
            self._writer.write(data)
            if not self._writer.is_closing():
                await self._writer.drain()
        if failed:
            logger.info("Thanks! It did not go well...")
        else:
            logger.info("Beautiful, thanks!")
            if self._gui is not None:
                self._gui.set_signal_level(None)
        if self._receive_task.done():  # lost connection to server
            self._change_state(GuiState.DISCONNECTED)
        else:
            self._change_state(GuiState.READY)

    async def _open_settings(self):
        my_assert(self._gui is not None, "settings button pressed without a GUI...")
        self._change_state(GuiState.SETTINGS)  # after this, the receiver is paused.
        server_settings = self._config['server'], str(self._config['port']), \
            self._config.get('name'), self._config.get('group')
        self._gui.open_settings(self._config)
        if self._writer is not None and not self._writer.is_closing():
            logger.debug("send initial keep-alive to server from open settings")
            self._writer.write(AdpcmEncoder.silence_frame(FrameType.KEEPALIVE))
        event = None
        while event is None:
            try:
                event = await asyncio.wait_for(self._events.get(), timeout=KEEPALIVE_INTERVAL)
            except asyncio.TimeoutError:
                if self._writer is not None and not self._writer.is_closing():
                    logger.debug("send keep-alive to server from open settings")
                    self._writer.write(AdpcmEncoder.silence_frame(FrameType.KEEPALIVE))
        my_assert(event == GuiEvent.GUI_READY.value, f"Unexpected event {event}")
        self._latency = int(self._config['latency'])
        logger.debug(f"got GUI ready event; settings closed, latency is {self._latency}, "
                     f"gain is {to_gain(self._config.get('gain', 0))}")
        if server_settings != (self._config['server'], str(self._config['port']),
                               self._config.get('name'), self._config.get('group')):
            logger.info(f"New server settings: {self._config['server']}:{self._config['port']}")
            if self._receive_task is not None and not self._receive_task.done():
                self._receive_task.cancel()
                self._writer.close()
            self._change_state(GuiState.CONNECTING)
            await self._connect_to_server()
        elif self._receive_task is None or self._receive_task.done():  # attempt a reconnection
            self._change_state(GuiState.CONNECTING)
            await self._connect_to_server()
        else:
            self._change_state(GuiState.READY, "Uncalibrated!" if self._latency == 0 else None)

    async def _connect_to_server(self) -> bool:
        # Connect to server
        try:
            self._reader, self._writer = await asyncio.open_connection(self._config['server'],
                                                                       int(self._config['port']))
        except ValueError as e:
            logger.error(f"Bad server settings {e}")
            self._change_state(GuiState.DISCONNECTED)
            return False
        except OSError as e:
            logger.warning(f"Connection failed with error {e}")
            self._change_state(GuiState.DISCONNECTED)
            return False
        logger.info(f"Connected to server {self._config['server']}:{self._config['port']} "
                    f"from {self._writer.get_extra_info('sockname')}")
        set_socket_settings(self._writer)

        # Authenticate
        self._writer.write(AuthenticationHeader(self._config.get('name', ''), self._config.get('group', '')).to_bytes())
        await self._writer.drain()

        # Start receiver
        self._change_state(GuiState.READY, "Uncalibrated!" if self._latency == 0 else None)
        self._receive_task = asyncio.create_task(self._receive_audio())
        return True

    async def main(self):
        self._audio = AudioIOStream()
        self._events = asyncio.Queue()
        self._state_changed = asyncio.Event()
        if self._gui:
            self._gui.events_out = self._events
            self._gui.loop = asyncio.get_event_loop()
        logger.info(f"Starting slave client v{VERSION}")
        await self._connect_to_server()

        # Event loop
        logger.debug("Start waiting for events")
        async for event in iterate_queue(self._events, poll_interval_s=KEEPALIVE_INTERVAL):
            if event is not None:
                assert isinstance(event, int)
                event = GuiEvent(event)

                if event == GuiEvent.SESSION_STARTS:
                    logger.debug("Got session start event")
                    await self._record_session()

                elif event == GuiEvent.SETTINGS_BUTTON:
                    if self._state not in (GuiState.READY, GuiState.DISCONNECTED):
                        continue  # skip button presses that are not in the right state
                    logger.debug("Got settings button event")
                    await self._open_settings()

                else:
                    logger.error(f"Not implemented: {event}")

            # check if receive_task is still alive
            if self._state != GuiState.READY:
                continue  # don't check if we are disconnected
            try:
                receive_exception = self._receive_task.exception()
            except asyncio.InvalidStateError:  # up and running, yeay!
                logger.debug("send keep-alive to server")
                self._writer.write(AdpcmEncoder.silence_frame(FrameType.KEEPALIVE))
                continue
            if receive_exception is not None:
                f = StringIO()
                self._receive_task.print_stack(file=f)
                logger.error(f"Receive task died with exception {receive_exception}, traceback {f.getvalue()}")
                self._change_state(GuiState.ERROR)
                break
            else:
                logger.warning("Got disconnected")
                self._change_state(GuiState.DISCONNECTED)

        # clean up before exit
        if self._writer is not None:
            self._writer.close()
        if self._receive_task is not None:
            logger.debug("waiting for receiver to complete")
            await self._receive_task
        return


def main(*, server: str, port: int, latency: int):
    config = {'server': server, 'port': port, 'latency': latency}
    client = SlaveClient(config, None)
    asyncio.run(client.main())
    exit(0)
