from audalign.recognizers import BaseRecognizer
from audalign.config.correlation_spectrogram import CorrelationSpectrogramConfig
from audalign.recognizers.correcognizeSpectrogram.correcognize_spectrogram import (
    correcognize,
    correcognize_directory,
)

import os
import typing
import copy
from functools import partial


class CorrelationSpectrogramRecognizer(BaseRecognizer):
    """Uses cross correlation on spectrogram to find alignment"""

    config: CorrelationSpectrogramConfig

    def __init__(self, config: CorrelationSpectrogramConfig = None):
        self.config = CorrelationSpectrogramConfig() if config is None else config
        self.last_recognition = None

    def recognize(
        self,
        file_path: str,
        against_path: str,
    ):
        if os.path.isdir(file_path):
            raise ValueError(f"file_path {file_path} must be a file")
        if os.path.isdir(against_path):
            recognition = correcognize_directory(file_path, against_path, self.config)
        else:
            recognition = correcognize(file_path, against_path, self.config)
        self.last_recognition = recognition
        return recognition

    def check_align_hook(
        self,
        file_list,
        dir_or_list,
        target_aligning: bool,
        fine_aud_file_dict: typing.Optional[dict],
    ):
        if self.config.multiprocessing == True and not target_aligning:
            return True
        return False

    def align_hook(
        self,
        file_list,
        dir_or_list,
        target_aligning: bool,
        fine_aud_file_dict: typing.Optional[dict],
    ):
        temp_config = copy.deepcopy(self.config)
        temp_config.multiprocessing = False
        temp_config.plot = False

        return partial(
            correcognize_directory,
            against_directory=dir_or_list,
            config=temp_config,
            _file_audsegs=fine_aud_file_dict,
            _include_filename=True,
        )

    def _align(self, file_path, dir_or_list):
        return correcognize_directory(file_path, dir_or_list, self.config)
