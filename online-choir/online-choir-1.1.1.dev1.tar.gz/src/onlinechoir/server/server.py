"""
The server backend.
"""
import asyncio
import audioop
from collections import deque
from typing import Optional

from ..common.audio_codecs import StereoEncoder, AudioEncoder, StereoDecoder, AdpcmDecoder
from ..common.constants import CONNECTION_TIMEOUT, SLAVE_PLAYBACK_BUFFER_SIZE, CHUNKS_PER_SECOND
from ..common.version import VERSION
from ..common.auth import HEADER_SIZE, AuthenticationHeader
from ..common.log import logger
from ..common.message_protocol import MessageProtocol
from ..common.network import set_socket_settings
from ..common.utils import iterate_stream, my_assert
from .audio_broadcaster import AudioBroadcaster
from .audio_mixer import AudioMixer
from .web_radio import WebRadio

CHECK_IN_TIMEOUT = 5  # seconds
MONITOR_QUEUE_SIZE = SLAVE_PLAYBACK_BUFFER_SIZE + int(CHUNKS_PER_SECOND) + 1


class MixServer:
    def __init__(self, master_port: int, slave_port: int, control_port: int, *,
                 ices_config: Optional[str] = None,
                 monitor_level: Optional[float] = None,
                 record_audio: bool = False,
                 safe: bool = True):
        self.mixer = AudioMixer(record_audio)
        self.broadcaster = AudioBroadcaster()
        self.radio = None
        self.monitor_level = monitor_level
        self.ready_for_session = asyncio.Event()
        self._master_port = master_port
        self._slave_port = slave_port
        self._control_port = control_port
        self._ices_config = ices_config
        self._master_server = None
        self._slave_server = None
        self._control_server = None
        self._safe = safe

    async def _send_mix_to_master(self, writer):
        try:
            while True:
                data = await self.mixer.get_frame()
                writer.write(data)
                await writer.drain()
        except ConnectionResetError:
            logger.debug("connection to master reset")

    async def _forward_audio_to_client(self, writer, source_id):
        while True:
            data = await self.broadcaster.get_frame(source_id)
            writer.write(data)
            await writer.drain()

    async def _serve_master(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        set_socket_settings(writer)
        try:
            header = AuthenticationHeader.from_bytes(await reader.readexactly(HEADER_SIZE))
        except (asyncio.IncompleteReadError, ConnectionResetError):
            logger.warning("Master did not send auth packet")
            writer.close()
            return
        if not header.is_valid:
            logger.warning("Invalid master client connected")
            writer.close()
            return
        if not self.ready_for_session.is_set():
            logger.warning("Second master attempted to join")
            writer.write(AudioEncoder.silence_frame(-2))  # terminate session immediately
            await writer.drain()
            return
        if self.mixer.num_sources == 0:
            logger.warning("Master attempted to join while there is no source")
            writer.write(AudioEncoder.silence_frame(-2))  # terminate session immediately
            await writer.drain()
            return
        logger.info(f"Master ({header.client_version}) joined from {writer.get_extra_info('peername')}")
        self.ready_for_session.clear()
        self.mixer.reset()
        self.broadcaster.reset()
        if self.monitor_level is not None:
            self.mixer.register_source(("monitor",), name='Monitor', gain=self.monitor_level)
            self.mixer.check_in(("monitor",))  # check in immediately
            decoder = StereoDecoder()
            monitor_queue = deque(maxlen=MONITOR_QUEUE_SIZE)
        mix_sender = asyncio.create_task(self._send_mix_to_master(writer))

        def check_for_active_slaves():
            logger.debug("checking for active sources")
            if self.mixer.num_active_sources == 0:
                logger.warning("No slave checked in, abort")
                mix_sender.cancel()
                writer.write(AudioEncoder.silence_frame(-2))  # terminate session immediately
                writer.close()
                self.broadcaster.reset()

        last_frame = -1
        got_end_frame = False
        checker = None
        async for data in iterate_stream(reader, StereoDecoder.PACKET_SIZE):
            idx = StereoDecoder.peek_frame_index(data)
            if idx < 0:
                logger.debug("  got end frame")
                got_end_frame = True
                self.mixer.set_end_frame(last_frame)
            else:
                my_assert(idx == last_frame + 1, "wrong idx")
                if idx == 0:
                    # Launch timer to check
                    logger.debug("Starting timer for check-ins")
                    checker = asyncio.get_event_loop().call_later(CHECK_IN_TIMEOUT, check_for_active_slaves)
                last_frame = idx
                if self.monitor_level is not None:  # send audio to the mix, too
                    left, right = decoder.decode_left_right(data, 3)
                    sig = audioop.add(audioop.mul(left, 3, 0.5), audioop.mul(right, 3, 0.5), 3)
                    if len(monitor_queue) == monitor_queue.maxlen:
                        self.mixer.inject_raw_frame(("monitor",), *monitor_queue.pop())
                    monitor_queue.appendleft((idx, sig))
            self.broadcaster.add_input_frame(data)
            if self.radio:
                self.radio.add_data(data)

        # connection closed
        if not got_end_frame:  # this only happens when the master drops abruptly
            logger.warning("  master closed early")
            self.broadcaster.add_input_frame(StereoEncoder.silence_frame(-1))
            self.mixer.set_end_frame(last_frame)
        mix_sender.cancel()  # Normally master closes when the whole mix has been received
        if self.monitor_level is not None:
            self.mixer.unregister_source(("monitor",))  # monitor the audio sent
        self.ready_for_session.set()
        if checker is not None:
            checker.cancel()
        logger.info("Master left")

    async def _serve_slave(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        set_socket_settings(writer)
        try:
            header = AuthenticationHeader.from_bytes(await reader.readexactly(HEADER_SIZE))
        except (asyncio.IncompleteReadError, ConnectionResetError):
            logger.warning("Slave did not send auth packet")
            writer.close()
            return
        if not header.is_valid:
            logger.warning("Invalid slave client connected")
            writer.close()
            return
        client_id = writer.get_extra_info('peername')
        logger.info(f"Client {client_id} ({header.name}, {header.group}, {header.client_version}) connected")
        self.broadcaster.register_client(client_id)
        self.mixer.register_source(client_id, name=header.name, group=header.group)
        audio_sender = asyncio.create_task(self._forward_audio_to_client(writer, client_id))
        try:
            async for data in iterate_stream(reader, AdpcmDecoder.PACKET_SIZE, timeout=CONNECTION_TIMEOUT):
                self.mixer.add_frame(client_id, data)
        except asyncio.CancelledError:
            logger.warning(f"Closing connection with {client_id}")
        except Exception as e:
            logger.info(f"Connection with {client_id} lost (error: {e})")
        finally:
            audio_sender.cancel()
            self.mixer.unregister_source(client_id)
            self.broadcaster.unregister_client(client_id)
            logger.info(f"Client {client_id} disconnected")
            writer.close()

    async def _serve_controller(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        set_socket_settings(writer)
        try:
            header = AuthenticationHeader.from_bytes(await reader.readexactly(HEADER_SIZE))
        except (asyncio.IncompleteReadError, ConnectionResetError):
            logger.warning("Controller did not send auth packet")
            writer.close()
            return
        if not header.is_valid:
            logger.warning("Invalid controller connected")
            writer.close()
            return
        logger.info(f"Controller ({header.client_version}) joined from {writer.get_extra_info('peername')}")
        while True:
            try:
                l = await reader.readexactly(2)
                msg = MessageProtocol.from_bytes(await reader.readexactly(MessageProtocol.get_length(l)))
                logger.debug(f"Received command {msg.msg}")
            except (ConnectionResetError, ValueError, asyncio.IncompleteReadError):
                break
            response = self.mixer.process_command(msg.msg)
            if response is not None:
                writer.write(MessageProtocol(response).to_bytes())
                await writer.drain()
        logger.info("Controller left")

    async def __aenter__(self):
        self._master_server = await asyncio.start_server(self._serve_master, port=self._master_port)
        self._slave_server = await asyncio.start_server(self._serve_slave, port=self._slave_port)
        self._control_server = await asyncio.start_server(self._serve_controller, port=self._control_port)

        if self._ices_config is not None and WebRadio.is_available():
            self.radio = WebRadio(self._ices_config)
        await self._master_server.__aenter__()
        await self._slave_server.__aenter__()
        await self._control_server.__aenter__()
        logger.info(f"Server v{VERSION} started")
        self.ready_for_session.set()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        logger.info("Stopping server")

        # wait for session to complete
        if self._safe and not self.ready_for_session.is_set():
            logger.info("Session in progress, waiting...")
            await self.ready_for_session.wait()

        # close radio channel
        if self.radio:
            self.radio.close()

        # ramp down servers
        await self._control_server.__aexit__(exc_type, exc_val, exc_tb)
        await self._slave_server.__aexit__(exc_type, exc_val, exc_tb)
        await self._master_server.__aexit__(exc_type, exc_val, exc_tb)

    async def serve_forever(self):
        await self._master_server.serve_forever()
        await self._slave_server.serve_forever()
        await self._control_server.serve_forever()


async def start_server(monitor_level: Optional[float],
                       master_port: int,
                       slave_port: int,
                       control_port: int,
                       record_audio: bool,
                       ices_config: Optional[str]):
    server_object = MixServer(master_port, slave_port, control_port,
                              record_audio=record_audio,
                              monitor_level=monitor_level,
                              ices_config=ices_config)
    async with server_object:
        await server_object.serve_forever()
