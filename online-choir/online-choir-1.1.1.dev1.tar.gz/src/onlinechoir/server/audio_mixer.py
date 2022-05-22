import asyncio
import audioop
from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Tuple, Optional, Iterable, Any

from ..common.log import logger
from ..common.platform import get_log_folder
from ..common.audio_codecs import AdpcmDecoder, AudioEncoder
from ..common.constants import CHUNKS_PER_SECOND, CHUNKS_IN_FLIGHT, SLAVE_PLAYBACK_BUFFER_SIZE, FrameType, FRAME_SIZE, \
    VOCAL_GROUPS
from ..common.utils import flush_queue, my_assert

MIX_WINDOW_SIZE = CHUNKS_IN_FLIGHT - SLAVE_PLAYBACK_BUFFER_SIZE - int(CHUNKS_PER_SECOND)
RAW_CHUNK_SIZE = 3 * FRAME_SIZE


@dataclass
class SourceInfo:
    name: str
    group: str
    gain: float
    decoder: Optional[AdpcmDecoder]
    buffer: Dict[int, bytes]

    @property
    def checked_in(self):
        return self.decoder is not None


class AudioMixer:
    def __init__(self, record_audio=False):
        self._sources: Dict[Tuple, SourceInfo] = {}
        self.mix_queue = asyncio.Queue()
        self.encoder = None
        self.mix_gain = None
        self.last_sources = None
        self.end_frame = None
        self.recording = [] if record_audio else None

    def register_source(self, source_id: Tuple, *, name: str = '', group: str = VOCAL_GROUPS[0], gain: float = 1.0):
        my_assert(source_id not in self._sources, f"source {source_id} already registered")
        self._sources[source_id] = SourceInfo(name, group, gain, None, {})

    def unregister_source(self, source_id: Tuple):
        was_active = self._sources[source_id].checked_in
        del self._sources[source_id]

        if self.mix_in_progress and was_active:  # if there are sill other sources, make sure the mix is up-to-date
            logger.debug(f"Trigger update after {source_id} left")
            self._update_mix()

    def reset(self):
        self.encoder = None
        self.mix_gain = None
        self.end_frame = None
        for source in self._sources.values():
            source.decoder = None
            source.buffer = {}
        flush_queue(self.mix_queue)
        if self.recording is not None:
            self.recording = []

    @property
    def num_sources(self):
        return len(self._sources)

    @property
    def num_active_sources(self):
        return sum(source.checked_in for source in self._sources.values())

    @property
    def mix_in_progress(self) -> bool:
        return self.encoder is not None

    def check_in(self, source_id: Tuple):
        logger.info(f"Source {source_id} checked in")
        self._sources[source_id].decoder = AdpcmDecoder()

    def check_out(self, source_id: Tuple):
        logger.info(f"Source {source_id} left the session (next_index was: "
                    f"{self._sources[source_id].decoder.next_index})")
        self._sources[source_id].decoder = None

    def _add_raw_frame(self, source_id: Tuple, idx: int, sig: bytes):
        if not self.mix_in_progress or idx >= self.encoder.next_index:  # store frames that are still useful
            buffer = self._sources[source_id].buffer
            my_assert(idx not in buffer, "duplicate frame idx")
            buffer[idx] = sig

    def inject_raw_frame(self, source_id: Tuple, idx: int, sig: bytes):
        my_assert(len(sig) == RAW_CHUNK_SIZE, "Wrong raw data size")
        decoder = self._sources[source_id].decoder
        my_assert(idx == decoder.next_index, "Wrong frame idx")
        decoder.next_index += 1  # fake decoding
        self._add_raw_frame(source_id, idx, sig)

    def add_frame(self, source_id: Tuple, frame: bytes):
        idx = AdpcmDecoder.peek_frame_index(frame)
        if idx == FrameType.KEEPALIVE:
            return   # ignore keepalive
        if not self._sources[source_id].checked_in:
            # accept joins while the mix has not been started
            if idx == FrameType.CHECK_IN:
                if not self.mix_in_progress:
                    self.check_in(source_id)
                else:
                    logger.warning(f"Source {source_id} checked in too late")
        else:
            if idx == FrameType.ABORT:  # drop from session
                self.check_out(source_id)
            else:
                exp = self._sources[source_id].decoder.decompress(frame, 3)
                self._add_raw_frame(source_id, idx, exp)

        # possibly produce a new mix frame
        self._update_mix()

    def set_end_frame(self, end_frame_idx: int):
        my_assert(self.end_frame is None, "duplicate end frame")
        logger.debug(f"Setting end frame to {end_frame_idx}")
        self.end_frame = end_frame_idx

    async def get_frame(self):
        frame = await self.mix_queue.get()
        return frame

    def _update_mix(self):
        """This function updates the status of the mix after a frame has been received or a client left"""
        if not self.mix_in_progress:
            # no mix in progress:
            # * check if all checked in
            # * if not, start if fastest client is about to dry out
            num_active_sources = self.num_active_sources
            if num_active_sources == self.num_sources:
                logger.debug("All in!")
                self._start_mix()
            elif num_active_sources > 0:
                bar = min(MIX_WINDOW_SIZE, self.end_frame or MIX_WINDOW_SIZE)
                _, idx_tip = self._quorum()
                if idx_tip >= bar:
                    self._start_mix()

        if self.mix_in_progress:
            # mix in progress:
            # * if all sources have dropped, close the mix
            # * see if mix frame(s) can be produced
            # * if all frames have been produced, close the mix
            # * drop used frames from buffers
            if self.num_active_sources == 0:
                # If all sources have left, interrupt
                logger.warning("All sources have left, interrupting")
                self.mix_queue.put_nowait(self.encoder.silence_frame(-2))
                return
            frame_ready = self._get_ready_idx()
            if frame_ready >= self.encoder.next_index:
                for idx in range(self.encoder.next_index, frame_ready + 1):
                    self._produce_frame(idx)
                if self.end_frame is not None and frame_ready == self.end_frame:
                    logger.info("Mixed last frame")
                    if self.recording:
                        self._dump_audio()

    def _start_mix(self):
        # * freeze mix gain
        my_assert(not self.mix_in_progress, "Mix already started")
        active_sources = {source_id: source.decoder.next_index
                          for source_id, source in self._sources.items() if source.checked_in}
        logger.info(f"Starting mix with {active_sources}")
        self.encoder = AudioEncoder()
        self.mix_gain = len(active_sources)
        self.last_sources = frozenset(active_sources)

    def _get_ready_idx(self):
        idx_ready, idx_tip = self._quorum()
        if self.end_frame is not None and idx_tip >= self.end_frame:
            # the fastest source has completed the track. Finish the mix.
            return self.end_frame
        return max(idx_ready, idx_tip - MIX_WINDOW_SIZE)

    def _produce_frame(self, idx: int):
        frames_to_mix = {}
        sources_status = {}
        for source_id, source in self._sources.items():
            if not source.checked_in:
                continue  # inactive source
            sources_status[source_id] = source.decoder.next_index
            if source.decoder.next_index <= idx:
                continue
            my_assert(idx in source.buffer, f"Frame {idx} not found in buffer of {source_id}")
            frames_to_mix[source_id] = (source.gain, source.buffer.pop(idx))
        active_sources = frozenset(frames_to_mix)
        if active_sources != self.last_sources:
            logger.debug(f"Producing mix frame {idx} with {len(frames_to_mix)} sources {sources_status}")
            self.last_sources = active_sources
        mix_frame = self.mix_frames(frames_to_mix.values(), self.mix_gain)
        self.mix_queue.put_nowait(self.encoder.create_frame(mix_frame))
        if self.recording is not None:
            self.recording.append(mix_frame)

    def _quorum(self) -> Tuple[int, int]:
        lasts = tuple(source.decoder.next_index - 1 for source in self._sources.values() if source.checked_in)
        return min(lasts), max(lasts)

    def _dump_audio(self):
        from common.audio_files import save_audio_file
        fname = get_log_folder() / f"recording_{datetime.now().strftime('%Y-%m-%d-%H:%M:%S')}.flac"
        logger.info(f"Saving mix under {fname}")
        save_audio_file(fname, b''.join(self.recording))
        self.recording = []

    @staticmethod
    def mix_frames(frames: Iterable[Tuple[float, bytes]], mix_gain: float) -> bytes:
        mix = None
        for gain, sig in frames:
            adj = audioop.mul(sig, 3, gain / mix_gain)
            if mix is None:
                mix = adj
            else:
                mix = audioop.add(mix, adj, 3)
        return audioop.lin2lin(mix, 3, 2)

    def process_command(self, command: Dict[str, Any]):
        action = command.get('action', 'none')
        if action == 'list':
            response = []
            for source_id, source in self._sources.items():
                if not source.checked_in:
                    continue
                response.append({'id': source_id, 'name': source.name, 'group': source.group,
                                 'gain': source.gain})
            logger.debug("sending list of active sources")
            return response
        if action == 'adjust_gain':
            source_id = tuple(command.get('id', ()))
            if source_id not in self._sources:
                logger.error(f"bad target {source_id}")
                return None
            try:
                gain = float(command['gain'])
            except (ValueError, KeyError):
                logger.error("invalid gain")
                return None
            logger.debug(f"change gain of source {source_id} to {gain}")
            self._sources[source_id].gain = gain
            return None
        logger.error(f"invalid action {action}")
        return None
