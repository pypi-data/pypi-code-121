import atexit
import importlib
import io
import os
import threading
from typing import Optional

import vessl
from vessl.util import logger
from vessl.util.audio import Audio
from vessl.util.common import get_module
from vessl.util.image import Image

MODE_TENSORFLOW2 = "mode-tf2"
MODE_OTHERS = "mode-others"

# Tensorboard event types
EVENT_TYPE_COMPRESSED_HISTOGRAMS = "distributions"
EVENT_TYPE_HISTOGRAMS = "histograms"
EVENT_TYPE_IMAGES = "images"
EVENT_TYPE_AUDIO = "audio"
EVENT_TYPE_SCALARS = "scalars"
EVENT_TYPE_TENSORS = "tensors"

# EventAccumulator argument (0 = keep all, N = keep N)
SIZE_GUIDANCE = {
    EVENT_TYPE_COMPRESSED_HISTOGRAMS: 1,
    EVENT_TYPE_IMAGES: 0,
    EVENT_TYPE_AUDIO: 0,
    EVENT_TYPE_SCALARS: 0,
    EVENT_TYPE_HISTOGRAMS: 1,
    EVENT_TYPE_TENSORS: 1,
}

READ_INTERVAL_IN_SEC = 1


class TensorboardCollector:
    """TensorboardCollector checks for new tensorboard events written to logdir and
    logs them to experiment metrics.

    There are two modes: `MODE_TENSORFLOW2` (TF2) and `MODE_OTHERS` (TF1, PyTorch, etc).
    `MODE_OTHERS` uses tensorboard's `EventAccumulator` to read from the event file.
    `MODE_TENSORFLOW2` uses tensorflow's `summary_iterator` because TF2 records events
      in a different way.
    """

    __slots__ = [
        "_exit",
        "_thread",
        "_tf_dict",
        "_event_accumulator",
    ]

    def start(self):
        self._start_thread()

    @property
    def _mode(self):
        if hasattr(self, "_tf_dict"):
            return MODE_TENSORFLOW2
        if hasattr(self, "_event_accumulator"):
            return MODE_OTHERS
        return ""

    def _is_initialized(self):
        return self._mode in (MODE_TENSORFLOW2, MODE_OTHERS)

    def _start_thread(self):
        def exit_fn(*args):
            self._exit.set()
            self._thread.join()
            if not self._is_initialized():
                logger.warn("No tensorboard writer was detected during the run.")

        atexit.register(exit_fn)

        self._exit = threading.Event()
        self._thread = threading.Thread(target=self._thread_body, daemon=True)
        self._thread.start()

    def _thread_body(self):
        while not self._exit.is_set():
            self._main()
            self._exit.wait(timeout=READ_INTERVAL_IN_SEC)
        self._main()

    def _main(self):
        if not self._is_initialized():
            # Wait for initialization
            return

        if self._mode == MODE_TENSORFLOW2:
            self._main_tensorflow2()

        elif self._mode == MODE_OTHERS:
            self._main_others()

    def _main_tensorflow2(self):
        """Main thread body for MODE_TENSORFLOW2"""
        # Skip already seen events
        for _ in range(self._tf_dict["start_index"]):
            try:
                next(self._tf_dict["summary_iterator"])
            except StopIteration:
                continue

        events = []
        for e in self._tf_dict["summary_iterator"]:
            events.append(e)

        self._tf_dict["start_index"] += len(events)
        for e in events:
            self._handle_event(e)

    def _handle_event(self, event):
        for val_struct in event.summary.value:
            event_type = val_struct.metadata.plugin_data.plugin_name

            if event_type == EVENT_TYPE_SCALARS:
                event_value = self._tf_dict["make_ndarray_fn"](val_struct.tensor).item()

            elif event_type == EVENT_TYPE_IMAGES:
                PILImage = get_module(
                    "PIL.Image",
                    required='Pillow package is required. Run "pip install Pillow".',
                )
                # First two tensors are height and width, image bytestrings start
                # from third tensor.
                event_value = [
                    Image(data=PILImage.open(io.BytesIO(bs)), caption=val_struct.tag)
                    for bs in val_struct.tensor.string_val[2:]
                ]

            elif event_type == EVENT_TYPE_AUDIO:
                wave = get_module(
                    "wave", required='wave package is required. Run "pip install wave".'
                )
                np = get_module(
                    "numpy",
                    required='numpy package is required. Run "pip install numpy".',
                )

                event_value = []
                for bs in val_struct.tensor.string_val:
                    if not bs:
                        continue
                    wave_object = wave.open(io.BytesIO(bs))
                    data = np.frombuffer(
                        wave_object.readframes(wave_object.getnframes()),
                        dtype="float32",
                    )
                    vessl_audio = Audio(
                        data,
                        sample_rate=wave_object.getframerate(),
                        caption=val_struct.tag,
                    )
                    event_value.append(vessl_audio)

            else:
                continue

            payload = {val_struct.tag: event_value}
            vessl.log(payload=payload, step=event.step, ts=event.wall_time)

    def _main_others(self):
        """Main thread body for MODE_OTHERS"""
        try:
            self._event_accumulator.Reload()  # Loads each event at most once
        except Exception:
            # No metrics have been saved yet
            return

        event_tags = self._event_accumulator.Tags()
        # ex. {"scalars": ["loss", "accuracy"], "images": ["caption"]}

        self._handle_scalars(event_tags[EVENT_TYPE_SCALARS])
        self._handle_images(event_tags[EVENT_TYPE_IMAGES])
        self._handle_audios(event_tags[EVENT_TYPE_AUDIO])

    def _handle_scalars(self, tags):
        for tag in tags:
            scalars = self._event_accumulator.Scalars(tag)
            self._flush_scalars(tag)  # Flush right away
            for scalar in scalars:
                self._log_scalar(tag, scalar)

    def _flush_scalars(self, tag):
        with self._event_accumulator.scalars._mutex:
            scalars = self._event_accumulator.scalars
        with scalars._buckets[tag]._mutex:
            scalars._buckets[tag].items = []

    def _log_scalar(self, tag, scalar):
        payload = {tag: scalar.value}
        vessl.log(payload=payload, step=scalar.step, ts=scalar.wall_time)

    def _handle_images(self, tags):
        for tag in tags:
            images = self._event_accumulator.Images(tag)
            self._flush_images(tag)  # Flush right away
            for image in images:
                self._log_image(tag, image)

    def _flush_images(self, tag):
        with self._event_accumulator.images._mutex:
            images = self._event_accumulator.images
        with images._buckets[tag]._mutex:
            images._buckets[tag].items = []

    def _log_image(self, tag, image):
        PILImage = get_module(
            "PIL.Image",
            required='Pillow package is required. Run "pip install Pillow".',
        )

        vessl_image = Image(
            data=PILImage.open(io.BytesIO(image.encoded_image_string)), caption=tag
        )

        payload = {tag: vessl_image}
        vessl.log(payload=payload, step=image.step, ts=image.wall_time)

    def _handle_audios(self, tags):
        for tag in tags:
            audios = self._event_accumulator.Audio(tag)
            self._flush_audios(tag)  # Flush right away
            for audio in audios:
                self._log_audio(tag, audio)

    def _flush_audios(self, tag):
        with self._event_accumulator.audios._mutex:
            audios = self._event_accumulator.audios
        with audios._buckets[tag]._mutex:
            audios._buckets[tag].items = []

    def _log_audio(self, tag, audio):
        wave = get_module(
            "wave", required='wave package is required. Run "pip install wave".'
        )
        np = get_module(
            "numpy", required='numpy package is required. Run "pip install numpy".'
        )

        wave_object = wave.open(io.BytesIO(audio.encoded_audio_string))
        data = np.frombuffer(
            wave_object.readframes(wave_object.getnframes()), dtype="float32"
        )
        vessl_audio = Audio(data, sample_rate=int(audio.sample_rate), caption=tag)

        payload = {tag: vessl_audio}
        vessl.log(payload=payload, step=audio.step, ts=audio.wall_time)

    def set_logdir(self, logdir, mode):
        """Called when tensorboard writer is detected. Only the first logdir will be used."""
        if not self._is_initialized():
            logger.info(f"Tensorboard logdir detected: {logdir}.")
            if mode == MODE_TENSORFLOW2:
                self._initialize_mode_tensorflow2(logdir)
            elif mode == MODE_OTHERS:
                self._initialize_mode_others(logdir)
        else:
            logger.debug(
                f"Cannot use multiple tensorboard logdirs. {logdir} will be ignored."
            )

    def _initialize_mode_tensorflow2(self, logdir):
        try:
            from tensorflow import make_ndarray
            from tensorflow.compat.v1.train import summary_iterator
        except Exception:
            logger.error(
                f"Could not import tensorflow. Failed to integrate tensorboard."
            )
            return

        # Get most recent event file. The event file for this run will have been just
        # created (in `tf.python.ops.gen_summary_ops.create_summary_file_writer`).
        path = mtime = None
        for dirpath, _, file_names in os.walk(logdir):
            for file_name in file_names:
                file_path = os.path.join(dirpath, file_name)
                file_mtime = os.path.getmtime(file_path)
                if "tfevents" in file_name and (mtime is None or mtime < file_mtime):
                    path, mtime = file_path, file_mtime

        if path is None:
            logger.info(f"No event file found in logdir: {logdir}.")
            return

        # Dict for MODE_TENSORFLOW2 objects
        self._tf_dict = {
            "make_ndarray_fn": make_ndarray,
            "summary_iterator": summary_iterator(path),
            "start_index": 0,
        }

    def _initialize_mode_others(self, logdir):
        try:
            from tensorboard.backend.event_processing.event_accumulator import (
                EventAccumulator,
            )
        except Exception:
            logger.error(
                "Could not import tensorboard. (Please install using `pip install tensorboard` first.) Failed to integrate tensorboard.",
            )
        self._event_accumulator = EventAccumulator(logdir, size_guidance=SIZE_GUIDANCE)

        try:
            self._event_accumulator.Reload()
        except Exception:
            # Logdir doesn't exist yet
            return

        # Disregard preexisting tensorboard logs
        for type, tags in self._event_accumulator.Tags().items():
            if type == EVENT_TYPE_SCALARS:
                for tag in tags:
                    self._flush_scalars(tag)
            if type == EVENT_TYPE_IMAGES:
                for tag in tags:
                    self._flush_images(tag)
            if type == EVENT_TYPE_AUDIO:
                for tag in tags:
                    self._flush_audios(tag)

    def close(self):
        """Joins thread to stop collecting. Used by tests."""
        self._exit.set()
        self._thread.join()
        return


# Global variable to ensure only one `TensorboardCollector` is active
tensorboard_collector_instance: Optional[TensorboardCollector] = None


def integrate_tensorboard():
    """Integrate tensorboard

    This method is called from `vessl.init` and can also be called manually."""
    global tensorboard_collector_instance

    if tensorboard_collector_instance is not None:
        logger.warning("Tensorboard is already enabled.")
        return

    tensorboard_collector_instance = TensorboardCollector()
    tensorboard_collector_instance.start()

    _patch_create_summary_file_writer(tensorboard_collector_instance)
    _patch_event_file_writers(tensorboard_collector_instance)


def _patch_create_summary_file_writer(tc):
    module_name = "tensorflow.python.ops.gen_summary_ops"
    try:
        module = importlib.import_module(module_name)
    except Exception as e:
        logger.debug(f"Module {module_name} not found. Skipping patch...")
        return

    _create_summary_file_writer = module.create_summary_file_writer

    def custom_create_summary_file_writer(*args, **kwargs):
        ret = _create_summary_file_writer(*args, **kwargs)
        logdir = (
            kwargs["logdir"].numpy().decode("utf8")
            if hasattr(kwargs["logdir"], "numpy")
            else kwargs["logdir"]
        )
        # Calling `set_logdir` after `_create_summary_file_writer` ensures that the
        # event file has already been created. This is important because we use the
        # most recent file in `logdir` as our event file.
        tc.set_logdir(logdir, MODE_TENSORFLOW2)
        return ret

    module.create_summary_file_writer = custom_create_summary_file_writer
    logger.debug(f"Module {module_name} was successfully patched.")


def _patch_event_file_writers(tc):
    module_names = [
        "tensorflow.python.summary.writer.writer",  # TF1
        "tensorboard.summary.writer.event_file_writer",
        "torch.utils.tensorboard.writer",
        "tensorboardX.writer",
    ]

    for module_name in module_names:
        try:
            module = importlib.import_module(module_name)
        except Exception as e:
            logger.debug(f"Module {module_name} not found. Skipping patch...")
            continue

        _patch_event_file_writer(module, tc)
        logger.debug(f"Module {module_name} was successfully patched.")


def _patch_event_file_writer(module, tc):
    _EventFileWriter = module.EventFileWriter

    class CustomEventFileWriter(_EventFileWriter):
        def __init__(self, *args, **kwargs):
            # self.log_dir is set in super().__init__
            super(CustomEventFileWriter, self).__init__(*args, **kwargs)

            logdir = self.get_logdir()
            tc.set_logdir(logdir, MODE_OTHERS)

    module.EventFileWriter = CustomEventFileWriter
