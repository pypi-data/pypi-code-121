import asyncio
import numpy as np
import platform
import soundfile
import tkinter as tk
from enum import Enum
from functools import partial
from sounddevice import OutputStream, CallbackStop
from threading import Lock, Thread
from tkinter.filedialog import askopenfile, asksaveasfile
from tkinter.messagebox import showerror
from tkinter.ttk import Scale, Separator, Combobox
from typing import MutableMapping, Callable, Optional

from ..common.config import default_config, config_path
from ..common.audio_devices import get_device_list, get_device_index
from ..common.constants import SAMPLING_RATE, FRAME_SIZE
from ..common.audio_files import load_audio_file, is_m4a_supported, load_m4a_file
from ..common.log import logger
from ..common.message_board import MessageBoard
from ..common.utils import my_assert, to_gain, remove_non_ascii, find_first
from .master_client import MasterClient, prepare_queue
from .mixing_desk import MixingDesk


class MasterClientState(Enum):
    IDLE = 0
    PREVIEW = 1
    PLAY = 2


class MasterClientGui:
    def __init__(self, config: MutableMapping[str, str], save_config: Optional[Callable[[], None]] = None):
        self.config = config
        self.save_config = save_config
        self.input = None
        self.output = None

        # GUI
        self.root = tk.Tk()
        self.root.title(f"Online Choir")
        self.open = tk.Button(self.root, text="Open", command=self._open_file)
        self.open.pack()
        self.start_label = tk.Label(text="0:00")
        self.start_label.pack()
        self.start_point = Scale(self.root, from_=0.0, to=1.0, state=tk.DISABLED, command=self._set_start_point)
        self.start_point.pack(fill=tk.X)
        self.preview = tk.Button(self.root, text="Play Locally", command=self._preview, state=tk.DISABLED)
        self.preview.pack()
        self.play = tk.Button(self.root, text="Play to Everyone", fg="red",
                              command=partial(self._start_session, live=False), state=tk.DISABLED)
        self.play.pack()
        self.live = tk.Button(self.root, text="Live Session", fg="red", command=partial(self._start_session, live=True))
        self.live.pack()
        self.stop = tk.Button(self.root, text="Stop", command=self._stop, state=tk.DISABLED)
        self.stop.pack()
        self.cur_time = tk.Label(text=" ")
        self.cur_time.pack()
        self.prev_time = None
        self.listen = tk.Button(self.root, text="Play Recording", command=self._listen, state=tk.DISABLED)
        self.listen.pack()
        self.save = tk.Button(self.root, text="Save Recording...", command=self._save, state=tk.DISABLED)
        self.save.pack()
        self.desk_button = tk.Button(self.root, text="Open Mixing Desk", command=self._open_desk, state=tk.DISABLED)
        self.desk_button.pack()
        self.desk = None

        # Device selection
        Separator(self.root).pack(fill=tk.X)
        device_sel = tk.Frame(self.root)
        tk.Label(device_sel, text="Input device:").grid(row=1, column=1)
        in_devs, in_idx = get_device_list(self.config, 'in_device', out=False)
        self.in_device_name = Combobox(device_sel, state='readonly', values=in_devs)
        self.in_device_name.current(in_idx)
        self.in_device_name.bind("<<ComboboxSelected>>", self._switch_input)
        self.in_device_name.grid(row=1, column=2)
        tk.Label(device_sel, text="Output device:").grid(row=2, column=1)
        out_devs, out_idx = get_device_list(self.config, 'device', out=True)
        self.out_device_name = Combobox(device_sel, state='readonly', values=out_devs)
        self.out_device_name.current(out_idx)
        self.out_device_name.bind("<<ComboboxSelected>>", self._switch_output)
        self.out_device_name.grid(row=2, column=2)
        device_sel.pack(pady=5, padx=10)

        # Server selection
        Separator(self.root).pack(fill=tk.X)
        server_sel = tk.Frame(self.root)
        tk.Label(server_sel, text="Server address:").grid(row=1, column=1)
        self.server_address = tk.Entry(server_sel, width=20)
        self.server_address.insert(0, self.config['server'])
        self.server_address.grid(row=1, column=2)
        tk.Label(server_sel, text="Server port:").grid(row=2, column=1)
        self.server_port = tk.Entry(server_sel, width=5)
        self.server_port.insert(0, self.config['port'])
        self.server_port.grid(row=2, column=2)
        server_sel.pack(pady=5)

        self.state = None

        # Audio
        self.stream = None
        self.play_mutex = Lock()
        self.play_cursor = None
        self.master_client = None

        # GUI updates
        self.update_board = MessageBoard()
        self.gui_updater = Thread(target=self._update_gui, name='GUI updater')
        self.gui_updater.start()

    def spin(self):
        self.state = MasterClientState.IDLE
        self.root.mainloop()
        if self.desk is not None:
            self.desk.changes.close()
        self.update_board.close()
        self.gui_updater.join()
        self.state = None  # nullify state after the GUI has stopped

    def _open_file(self):
        f_types = (
            ("WAV files", "*.wav"),
            ("Ogg files", "*.ogg"),
            ("FLAC", "*.flac"),
        )
        if platform.system() == "Darwin":
            f_types += (("Mp3 files", "*.mp3"),)
        if is_m4a_supported():
            f_types += (("M4a files", "*.m4a"),)
        logger.info("Selecting input file")
        f = askopenfile(mode="rb", parent=self.root, title="Open Audio File", filetypes=f_types)
        if f is not None:
            try:
                self._open_audio(f)
            except (ValueError, OSError, RuntimeError, soundfile.LibsndfileError) as e:
                logger.error(f"Failed to open file: {e}")
                showerror(title="Open file", message="Could not open file")
            finally:
                f.close()

    def _clear_stream(self):
        my_assert(self.state == MasterClientState.IDLE, "Should be idle")
        if self.stream is not None:
            my_assert(not self.stream.active, f"Stream active={self.stream.active}")
            self.stream.close()
            self.stream = None

    def _preview(self):
        self._clear_stream()
        s = float(self.start_point.get())
        logger.info(f"Preview audio file from {s:.1f}s")
        self.play_cursor = int(round(s * 44100 / FRAME_SIZE) * FRAME_SIZE)
        self._change_state(MasterClientState.PREVIEW)
        self.stream = OutputStream(device=self._get_out_device(),
                                   samplerate=SAMPLING_RATE,
                                   blocksize=FRAME_SIZE,
                                   channels=2,
                                   dtype="float32",
                                   callback=self._player_callback,
                                   finished_callback=self._player_done,
                                   latency='high')
        self.stream.start()

    def _listen(self):
        self._clear_stream()
        logger.info(f"Listen to recording")
        self.play_cursor = 0
        self._change_state(MasterClientState.PREVIEW)
        self.stream = OutputStream(device=self._get_out_device(),
                                   samplerate=SAMPLING_RATE,
                                   blocksize=FRAME_SIZE,
                                   channels=1,
                                   dtype="float32",
                                   callback=self._listen_callback,
                                   finished_callback=self._player_done,
                                   latency='high')
        self.stream.start()

    def _start_session(self, live: bool):
        self.config['server'], self.config['port'] = self.server_address.get(), self.server_port.get()
        self._clear_stream()
        level_db = float(self.config.get('monitor_level', -10))
        level_abs = to_gain(level_db) if level_db > -35 else 0
        logger.info(f"Starting session! (monitor level = {level_abs})")
        self.master_client = MasterClient(mute=live, monitor_level=level_abs, gui_board=self.update_board,
                                          in_device=self._get_in_device(), out_device=self._get_out_device())
        self._change_state(MasterClientState.PLAY)

        async def run_client():
            if live:
                q = None
            else:
                q = prepare_queue(self.input, float(self.start_point.get()))
            try:
                await self.master_client.main(self.config['server'], int(self.config['port']), q)
            except OSError as e:
                msg = f"OSError {find_first(e.args, lambda x: isinstance(x, str), 'unknown error')}"
                logger.error(msg)
                return msg
            else:
                logger.info("Master logic completed")
                return None

        def run_client_thread():
            msg = asyncio.run(run_client())
            logger.debug("Client thread completed")
            if msg is None:
                self.output = self.master_client.get_recording()
            else:
                showerror(title="Connection Error", message=msg)
            self.master_client = None
            self._change_state(MasterClientState.IDLE)

        Thread(target=run_client_thread, name='master client').start()

    def _stop(self):
        logger.info("Stopping")
        self.stop.config(state=tk.DISABLED)  # prevent re-clicking of the button while process is stopping.
        if self.state == MasterClientState.PREVIEW:
            with self.play_mutex:
                self.play_cursor = max(len(self.input) if self.input is not None else 0,
                                       len(self.output) if self.output is not None else 0)
        elif self.state == MasterClientState.PLAY:
            self.master_client.stop()

    def _save(self):
        logger.info("Saving output")
        f = asksaveasfile(mode="wb", parent=self.root, title="Save Recording As...", defaultextension=".wav")
        if f is not None:
            self._save_audio(f)
            f.close()

    def _change_state(self, new_state: MasterClientState):
        my_assert(new_state != self.state, "Repeated state")
        logger.debug(f"Changing state to {new_state}")

        # disabling buttons
        if new_state == MasterClientState.IDLE:
            self.stop.config(state=tk.DISABLED)
            if self.save_config is not None:
                self.save_config()
        else:  # MasterClientState.PLAY, MasterClientState.PREVIEW
            self.open.config(state=tk.DISABLED)
            self.play.config(state=tk.DISABLED)
            self.live.config(state=tk.DISABLED)
            self.preview.config(state=tk.DISABLED)
            self.listen.config(state=tk.DISABLED)
            self.save.config(state=tk.DISABLED)

        self.state = new_state  # change state

        # enabling buttons
        if new_state == MasterClientState.IDLE:
            self.open.config(state=tk.NORMAL)
            if self.input is not None:
                self.play.config(state=tk.NORMAL)
                self.preview.config(state=tk.NORMAL)
            self.live.config(state=tk.NORMAL)
            if self.output is not None:
                self.listen.config(state=tk.NORMAL)
                self.save.config(state=tk.NORMAL)
        else:  # MasterClientState.PLAY, MasterClientState.PREVIEW
            self.stop.config(state=tk.NORMAL)

    def _open_audio(self, fd):
        if is_m4a_supported() and fd.name.endswith('.m4a'):
            self.input = load_m4a_file(fd.name)
        else:
            self.input = load_audio_file(fd)
        self.root.title(fd.name.split('/')[-1])
        self.preview.config(state=tk.NORMAL)
        self.play.config(state=tk.NORMAL)
        self.start_point.config(to=len(self.input) / 44100, state=tk.NORMAL)
        self.start_point.set(0.0)

    def _save_audio(self, fd):
        soundfile.write(fd, self.output, SAMPLING_RATE, format="WAV")

    def _player_callback(self, outdata: np.ndarray, frames: int, _, status):
        if status:
            logger.error(f"Audio callback error {status}")
        with self.play_mutex:
            cur = self.play_cursor
            self.play_cursor = cur + FRAME_SIZE
        if cur >= len(self.input):
            outdata[:, :] = 0
            raise CallbackStop
        outdata[:, :] = self.input[cur: cur + FRAME_SIZE, :]
        self.update_board.post_message('tick', cur)

    def _listen_callback(self, outdata: np.ndarray, frames: int, _, status):
        if status:
            logger.error(f"Audio callback error {status}")
        with self.play_mutex:
            cur = self.play_cursor
            self.play_cursor = cur + FRAME_SIZE
        if cur >= len(self.output):
            outdata[:, :] = 0
            raise CallbackStop
        outdata[:, 0] = self.output[cur: cur + FRAME_SIZE]
        self.update_board.post_message('tick', cur)

    def _player_done(self):
        logger.debug(f"Player done, status is active:{self.stream.active}, stopped:{self.stream.stopped}")
        self._change_state(MasterClientState.IDLE)

    def _set_monitor_level(self, fader_value: str):
        level_db = float(fader_value) - 35
        self.config['monitor_level'] = str(level_db)
        if self.master_client is not None:
            level_abs = to_gain(level_db) if level_db > -35 else 0
            self.master_client.set_monitor_level(level_abs)

    def _set_start_point(self, p):
        s = float(p)
        self.start_label.config(text=f"{int(s) // 60}:{s % 60:02.1f}")

    def _set_cur_time(self, frame: int):
        tick = int(round(frame / 4410))
        if tick != self.prev_time:
            self.cur_time.config(text=f"{int(tick) // 600}:{(tick % 600) / 10:02.1f}")
            self.prev_time = tick

    def _switch_input(self, _):
        new_input = remove_non_ascii(self.in_device_name.get())
        logger.info(f"Changing audio input to {new_input}")
        self.config['in_device'] = new_input

    def _switch_output(self, _):
        new_output = remove_non_ascii(self.out_device_name.get())
        logger.info(f"Changing audio output to {new_output}")
        self.config['device'] = new_output

    def _get_in_device(self) -> int:
        return get_device_index(self.config.get('in_device', ''), False)

    def _get_out_device(self) -> int:
        return get_device_index(self.config.get('device', ''), True)

    def _open_desk(self):
        if self.desk is None:
            logger.debug("open mixing desk")
            self.desk = MixingDesk(self.root, self.config, self._close_desk, self._set_monitor_level)
        else:
            self.desk.top.lift()

    def _close_desk(self):
        if self.desk is None:
            return
        logger.debug("close mixing desk")
        self.desk.destroy()
        self.desk = None

    def _update_gui(self):
        logger.debug("start GUI updater")
        for topic, content in self.update_board.messages():
            if topic == 'tick':
                self._set_cur_time(content)
            elif topic == 'session_active':
                if content:
                    self.desk_button.config(state=tk.NORMAL)
                    if self.desk is not None:
                        self.desk.trigger_update()
                else:
                    self.desk_button.config(state=tk.DISABLED)
            # elif topic == 'levels':
            #     if self.desk:
            #         self.desk.set_channel_levels(content)
        logger.debug("GUI updater ended")


def main():
    logger.info(f"Started on {platform.system()}")
    config = default_config()
    if 'master' not in config.sections():
        config['master'] = {'server': 'online-choir.modetexte.ch',
                            'port': '8878'}

    def save_config():
        logger.debug("Saving config")
        with config_path().open('w') as fd:
            config.write(fd)

    gui = MasterClientGui(config['master'], save_config)
    logger.debug("Start master GUI")
    gui.spin()
