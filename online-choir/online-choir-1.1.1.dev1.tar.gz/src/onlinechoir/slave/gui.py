import asyncio
import platform
import numpy as np
import soundfile as sf
import sounddevice as sd
import tkinter as tk
import threading
import traceback
from functools import partial
from io import StringIO
from queue import Queue
from pathlib import Path
from tkinter.messagebox import showerror
from tkinter.ttk import Separator, Scale, Combobox, Checkbutton, Spinbox, Style
from typing import Optional, Mapping

from .level_meter import BarLevelMeter, DotLevelMeter
from .db_calculator import DbCalculator
from ..common.audio_devices import get_device_list, get_device_index
from ..common.config import default_config, config_path
from ..common.constants import SAMPLING_RATE, FRAME_SIZE, VOCAL_GROUPS
from ..common.log import logger
from ..common.singleton import register_process, unregister_process
from ..common.utils import my_assert, remove_non_ascii
from .calibration_tool import generate_test_audio, MAX_LATENCY, calculate_latency
from .gui_enums import GuiEvent, GuiState
from .signal_smoother import SignalSmoother
from .slave_client import SlaveClient


# TODO:
# * test dead stream
# * handle bad config in sessions


class AudioSettings:
    def __init__(self, parent, destroy, config):
        self.top = tk.Toplevel(parent)
        self.top.title("Settings")
        self.top.protocol("WM_DELETE_WINDOW", destroy)
        self.config = config
        self.level_changes = Queue()
        self.level_updater = threading.Thread(target=self._level_updater, name='level updater')

        row = 0

        # Identity
        tk.Label(self.top, text="Singer Name:").grid(row=row, column=0, sticky='W')
        self.name = tk.Entry(self.top)
        self.name.insert(0, self.config.get('name', ''))
        self.name.grid(row=row, column=1, sticky='EW', padx=10)
        row += 1
        tk.Label(self.top, text="Vocal Group:").grid(row=row, column=0, sticky='W')
        self.vocal_group = Combobox(self.top, values=VOCAL_GROUPS, state='readonly')
        try:
            group_idx = VOCAL_GROUPS.index(self.config.get('group', ''))
        except ValueError:
            group_idx = 0
        self.vocal_group.current(group_idx)
        self.vocal_group.grid(row=row, column=1, sticky='EW', padx=10)
        row += 1

        # Input
        Separator(self.top).grid(row=row, column=0, columnspan=2, sticky='EW', pady=10)
        row += 1
        input_devices, cur_input = get_device_list(self.config, 'audio_input', False)
        tk.Label(self.top, text="Input device:").grid(row=row, column=0, sticky='W')
        self.input_selector = Combobox(self.top, values=input_devices, state='readonly')
        self.input_selector.current(cur_input)
        self.input_selector.bind("<<ComboboxSelected>>", self._switch_input)
        self.input_selector.grid(row=row, column=1, sticky='EW', padx=10)
        row += 1
        tk.Label(self.top, text="Input level:").grid(row=row, column=0, sticky='W')
        self.monitor = BarLevelMeter(self.top, row=row, column=1)
        row += 1
        tk.Label(self.top, text="Microphone Gain:").grid(row=row, column=0, sticky='W')
        gain = config.get('gain', 0)
        self._db_calculator = DbCalculator(gain_db=gain)
        level_scale = Scale(self.top, from_=-20, to=20, command=self._set_gain)
        level_scale.set(gain)
        level_scale.grid(row=row, column=1, sticky='EW', padx=10)
        row += 1

        # Output
        Separator(self.top).grid(row=row, column=0, columnspan=2, sticky='EW', pady=10)
        row += 1
        tk.Label(self.top, text="Output device:").grid(row=row, column=0, sticky='W')
        output_devices, cur_output = get_device_list(self.config, 'audio_output', True)
        self.output_selector = Combobox(self.top, values=output_devices, state='readonly')
        self.output_selector.current(cur_output)
        self.output_selector.bind("<<ComboboxSelected>>", self._switch_output)
        self.output_selector.grid(row=row, column=1, sticky='EW', padx=10)
        row += 1
        self.test = tk.Button(self.top, text="Play Sample Sound", command=self.test_output, state=tk.DISABLED)
        self.test.grid(row=row, column=0, columnspan=2)
        root_folder = Path(__file__).parent.resolve()
        self.sample_sig = np.zeros((345 * FRAME_SIZE, 2))
        try:
            sf.read(root_folder / "data" / "output_test.wav", out=self.sample_sig)
        except RuntimeError:
            msg = "Could not read src/onlinechoir/slave/data/output_test.wav. " \
                  "Did you set up git-lfs and checked it out correctly?"
            logger.error(msg)
            raise RuntimeError(msg)
        row += 1

        # Calibration
        Separator(self.top).grid(row=row, column=0, columnspan=2, sticky='EW', pady=10)
        row += 1
        Style().configure("Red.TSpinbox", background="red")
        tk.Label(self.top, text="Current latency:").grid(row=row, column=0, sticky='W')
        self.latency_box = Spinbox(self.top, increment=1, from_=0, to=200, command=self._latency_box_callback, width=4)
        self._set_latency(int(config['latency'] or 0))
        self.latency_box.grid(row=row, column=1, sticky='W', padx=10)
        row += 1
        tk.Label(self.top, text="A latency value of 0 means that the latency is undefined yet.\n"
                                "To measure the latency, place your headphones close\n"
                                "to the microphone, raise the volume and click below.\n"
                                "Do not change the latency value manually unless you know what you are doing!") \
            .grid(row=row, column=0, columnspan=2)
        row += 1
        self.calib = tk.Button(self.top, text="Measure Latency", command=self.calibrate, fg="red", state=tk.DISABLED)
        self.calib.grid(row=row, column=0, columnspan=2)
        row += 1
        tk.Label(self.top, text="Do not press the above button with the headphones on your ears!", fg="red") \
            .grid(row=row, column=0, columnspan=2)
        weep = generate_test_audio()
        self.weep_len, n_chan = weep.shape
        my_assert(n_chan == 2, "Wrong weep shape")
        self.out_signal = np.zeros((self.weep_len + FRAME_SIZE * MAX_LATENCY, 2), dtype=np.float32)
        self.out_signal[:self.weep_len, :] = weep
        self.in_signal = np.empty((self.weep_len + FRAME_SIZE * MAX_LATENCY,), dtype=np.float32)
        row += 1

        # Server selection
        Separator(self.top).grid(row=row, column=0, columnspan=2, sticky='EW', pady=10)
        row += 1
        tk.Label(self.top, text="Server address:").grid(row=row, column=0, sticky='W')
        self.server_address = tk.Entry(self.top, width=20)
        self.server_address.insert(0, self.config['server'])
        self.server_address.grid(row=row, column=1, sticky='W', padx=10)
        row += 1
        tk.Label(self.top, text="Server port:").grid(row=row, column=0, sticky='W')
        self.server_port = tk.Entry(self.top, width=5)
        self.server_port.insert(0, self.config['port'])
        self.server_port.grid(row=row, column=1, sticky='W', padx=10)
        row += 1

        # Close button
        Separator(self.top).grid(row=row, column=0, columnspan=2, sticky='EW', pady=10)
        row += 1
        self.ok = tk.Button(self.top, text="OK", command=destroy)
        self.ok.grid(row=row, column=0, columnspan=2)
        row += 1

        # Start audio stream
        self.mutex = threading.Lock()
        self.cursor = None
        self.rec = None
        self.stream = None
        self._start_stream(self.config.get('audio_input'), self.config.get('audio_output'))
        self.level_updater.start()

    def _start_stream(self, in_device: str, out_device: str):
        my_assert(self.stream is None, "Stream should be None")
        devices = (get_device_index(in_device, False), get_device_index(out_device, True))
        logger.debug(f"devices are {devices}")
        try:
            self.stream = sd.Stream(device=devices,
                                    samplerate=SAMPLING_RATE,
                                    blocksize=FRAME_SIZE,
                                    channels=(1, 2),
                                    dtype="float32",
                                    callback=self._player_callback,
                                    latency='high')
            self.stream.start()
        except (sd.PortAudioError, ValueError) as e:
            logger.error(f"Failed to start stream: {e}")
            return

    def _stop_stream(self):
        if self.stream is not None:
            self.test.config(state=tk.DISABLED)
            self.calib.config(state=tk.DISABLED)
            self.stream.close()
            self.level_changes.put_nowait(0)
            self.stream = None

    def _player_callback(self, indata: np.ndarray, outdata: np.ndarray, frames: int, _, status):
        # General switch: self.rec, self.cursor
        # None, None: idle
        # False, 0: request to play sample
        # True, 0: request to calibrate
        # False/True, >0: play
        # False/True, -1: process
        my_assert(frames == FRAME_SIZE, "wrong frame size")
        with self.mutex:
            rec = self.rec
            cursor = self.cursor
        if status:  # error case
            if rec and cursor >= 0:
                logger.error(f"callback error {status}, calibration failed")
                threading.Thread(target=self._processing, name='failed processing').start()  # cancel
            else:
                logger.debug(f"Got status {status}")
            return  # do nothing else

        if self.level_changes.empty():  # skip if updater is behind
            self.level_changes.put_nowait(indata.copy())

        if rec is None or cursor < 0:  # play silence, ignore input
            outdata[:] = 0.
            return

        my_assert(cursor is not None, "cursor not be None when rec is not None")
        sig = self.out_signal if self.rec else self.sample_sig
        outdata[:, :] = sig[self.cursor: self.cursor + FRAME_SIZE, :]
        if self.rec:  # is True
            self.in_signal[self.cursor: self.cursor + FRAME_SIZE] = indata[:, 0]
        self.cursor += FRAME_SIZE
        if self.cursor >= len(sig):
            logger.debug("Finished playing, start processor")
            self.cursor = -1
            threading.Thread(target=self._processing, name='processing').start()  # process the result

    def _set_latency(self, latency: int):
        self.latency_box.set(latency)
        self._update_latency_box_color(latency)

    def _latency_box_callback(self):
        self._update_latency_box_color(int(self.latency_box.get()))

    def _update_latency_box_color(self, value: int):
        if value > 0:
            self.latency_box.configure(style="TSpinbox")
        else:
            self.latency_box.configure(style="Red.TSpinbox")

    def _processing(self):
        my_assert(self.cursor is not None, "This thread should not start if cursor is None")
        my_assert(self.rec is not None, "This thread should not start if rec is None")
        if self.rec:
            if self.cursor == -1:  # recording complete
                latency = calculate_latency(self.out_signal[:self.weep_len].mean(axis=1),
                                            self.in_signal * self._db_calculator.gain)
                logger.info(f"Processing done. Latency is {latency or 'not measured successfully'}")
                self._set_latency(int(round(latency or 0)))
            else:  # recording incomplete
                logger.warning("Recording interrupted.")
        with self.mutex:
            self.rec = None
            self.cursor = None
        self.calib.config(state=tk.NORMAL)
        self.test.config(state=tk.NORMAL)
        self.ok.config(state=tk.NORMAL)
        self.latency_box.configure(state='normal')
        self.input_selector.configure(state='readonly')
        self.output_selector.configure(state='readonly')
        logger.debug("Processing completed")

    def _level_updater(self):
        logger.debug("Start level updater")
        stream_active = False
        while True:
            sample = self.level_changes.get()
            if sample is None:  # poison pill
                break
            if isinstance(sample, int):  # stream ended
                self.monitor.reset()
                stream_active = False
            else:  # actual numpy array
                if not stream_active:
                    self._stream_active()
                    stream_active = True
                db = self._db_calculator.from_sample(sample)
                self.monitor.update_level(db)
        logger.debug("End level updater")

    def _stream_active(self):
        self.test.config(state=tk.NORMAL)
        self.calib.config(state=tk.NORMAL)
        self.config['audio_input'] = remove_non_ascii(self.input_selector.get())
        self.config['audio_output'] = remove_non_ascii(self.output_selector.get())

    def _set_gain(self, gain: str):  # gain is in dB and is a string because it is a tkinter widget
        self.config['gain'] = gain
        self._db_calculator.set_gain(gain_db=gain)
        logger.debug(f"Gain set to {self._db_calculator.gain} ({self._db_calculator.gain_db} dB)")

    def test_output(self):
        logger.info("Testing output")
        self._busy()
        with self.mutex:
            self.rec = False
            self.cursor = 0

    def calibrate(self):
        logger.info("Calibrate")
        self._busy()
        with self.mutex:
            self.rec = True
            self.cursor = 0

    def _busy(self):
        self.calib.config(state=tk.DISABLED)
        self.test.config(state=tk.DISABLED)
        self.ok.config(state=tk.DISABLED)
        self.latency_box.configure(state='disabled')
        self.input_selector.configure(state='disabled')
        self.output_selector.configure(state='disabled')

    def _switch_input(self, _):
        new_input = self.input_selector.get()
        logger.info(f"Changing audio input to {remove_non_ascii(new_input)}")
        self._restart_audio(new_input, self.config.get('audio_output', ''))

    def _switch_output(self, _):
        new_output = self.output_selector.get()
        logger.info(f"Changing audio output to {remove_non_ascii(new_output)}")
        self._restart_audio(self.config.get('audio_input', ''), new_output)

    def _restart_audio(self, in_device: str, out_device: str):
        self._set_latency(0)
        logger.debug("Restarting audio stream")
        if self.rec is not None:
            logger.error("Cannot restart audio stream, as it is playing")
            return
        self._stop_stream()
        self._start_stream(in_device, out_device)

    def _get_name(self) -> str:
        lines = self.name.get().splitlines()
        if lines:
            return lines[0].strip()
        return ''

    def destroy(self):
        with self.mutex:
            playing = self.rec is not None
        if playing:
            return False
        self.level_changes.put_nowait(None)
        self.level_updater.join()
        self._stop_stream()
        self.config['server'] = self.server_address.get()
        self.config['port'] = self.server_port.get()
        self.config['name'] = self._get_name()
        self.config['group'] = self.vocal_group.get()
        self.config['latency'] = self.latency_box.get()
        self.top.destroy()
        return True


class SlaveClientGui:
    def __init__(self, save_config=None):
        self.events_out: Optional[asyncio.Queue] = None
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.save_config = save_config

        # create window
        self.root = tk.Tk()
        self.root.title(f"Online Choir")
        self.label = tk.Label(master=self.root, text="CONNECTING...")
        self.label.grid(row=1, column=1, padx=10, pady=10)

        self.mute = tk.IntVar(self.root, 1, 'mute')
        Checkbutton(self.root, text="Mute", variable=self.mute,
                    offvalue=1, onvalue=0).grid(row=2, column=1, padx=10, pady=10)
        self.button = tk.Button(master=self.root, text="Settings", width=20, state=tk.DISABLED,
                                command=partial(self.send_event, GuiEvent.SETTINGS_BUTTON.value))
        self.button.grid(row=3, column=1, columnspan=2, padx=10, pady=10)

        self.monitor = DotLevelMeter(self.root, row=1, column=2, padx=10, pady=10)

        # State variables
        self.state = None
        self.signal_smoother = SignalSmoother(-1)

        # Settings
        self.settings = None

    def spin(self):
        try:
            self.root.mainloop()
        finally:
            self.state = GuiState.DEAD  # nullify state after the GUI has stopped
            if self.loop.is_running():
                logger.debug("Sending null event to business logic")
                self.send_event(None)

    # this is to be called from another thread
    def change_state(self, state: int, message: Optional[str] = None):
        if self.state == GuiState.DEAD:
            return  # ignore post-mortem commands
        state = GuiState(state)
        my_assert(state != self.state, "repeated state")
        logger.info(f"Changing state to {state.name}")
        self.state = state
        text = state.name
        if message:
            text += f"({message})"
        self.label["text"] = text
        if state in (GuiState.READY, GuiState.DISCONNECTED):
            self.button.config(state=tk.NORMAL)
        else:
            self.button.config(state=tk.DISABLED)

    def send_event(self, event: Optional[int]):
        self.loop.call_soon_threadsafe(self.events_out.put_nowait, event)

    # this is to be called from another thread
    def set_signal_level(self, db: Optional[float]):
        if self.state == GuiState.DEAD:
            return  # ignore post-mortem commands
        self.monitor.update_level(db)

    def open_settings(self, config: Mapping[str, str]):
        self.settings = AudioSettings(self.root, self.close_settings, config)

    def close_settings(self):
        logger.debug("close settings")
        if self.settings.destroy():
            if self.save_config:
                self.save_config()
            self.send_event(GuiEvent.GUI_READY.value)
            self.settings = None
            return True
        return False


def main():
    logger.info(f"Started on {platform.system()}")
    try:
        register_process('singer_gui')
    except RuntimeError:
        showerror(message='Another instance of Online Choir is running')
        return
    config = default_config()
    if 'slave' not in config.sections():
        config['slave'] = {'server': 'online-choir.modetexte.ch',
                           'port': '8868',
                           'latency': '0'}
    logger.debug(f"Loaded config. Latency is {config['slave']['latency']}.")

    def save_config():
        logger.debug("Saving config")
        with config_path().open('w') as fd:
            config.write(fd)

    gui = SlaveClientGui(save_config)
    client = SlaveClient(config['slave'], gui)

    def run_business_logic():
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(client.main())
        except Exception as e:
            logger.error(f"Business logic crashed with error {e}")
            sf = StringIO()
            traceback.print_tb(e.__traceback__, file=sf)
            logger.debug(sf.getvalue())
            gui.change_state(GuiState.DISCONNECTED.value)
        finally:
            loop.close()
        return

    business_logic = threading.Thread(target=run_business_logic, name='business logic')
    logger.debug("Start business logic thread")
    business_logic.start()
    logger.debug("Start GUI")
    gui.spin()
    logger.debug("Wait for business logic to exit")
    business_logic.join()
    unregister_process('singer_gui')
    logger.debug("Done")
