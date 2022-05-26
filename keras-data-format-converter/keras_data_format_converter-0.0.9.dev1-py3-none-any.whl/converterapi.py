import logging
from typing import List

import tensorflow as tf
from tensorflow import keras

from keras_data_format_converter.modelconverter import ModelConverter
from keras_data_format_converter.utils import configure_logger


def convert_channels_first_to_last(model: keras.Model, inputs_to_transpose: List[str] = None, verbose: bool = False) \
        -> keras.Model:
    """
    Convert keras models from channels first to last

    :param inputs_to_transpose: list of input names to transpose
    :type inputs_to_transpose: List[str]
    :param verbose: by default true, set to False to lower the logging level
    :type verbose: bool
    :param model: keras model to convert in channels first format
    :type model: tensorflow.keras.Model
    :return: converted keras model in channels last format
    :rtype: tensorflow.keras.Model
    """
    target_data_format = "channels_last"
    return _convert_channels(model, target_data_format, inputs_to_transpose, verbose)


def convert_channels_last_to_first(model: tf.keras.Model, inputs_to_transpose: List[str] = None, verbose: bool = False) \
        -> tf.keras.Model:
    """
    Convert keras models from channels last to first

    :param inputs_to_transpose: list of input names to transpose
    :type inputs_to_transpose: List[str]
    :param verbose: by default true, set to False to lower the logging level
    :type verbose: bool
    :param model: keras model to convert in channels last format
    :type model: tensorflow.keras.Model
    :return: converted keras model in channels first format
    :rtype: tensorflow.keras.Model
    """
    target_data_format = "channels_first"
    return _convert_channels(model, target_data_format, inputs_to_transpose, verbose)


def _convert_channels(model: tf.keras.Model, target_data_format: str, inputs_to_transpose: List[str], verbose: bool) \
        -> tf.keras.Model:
    # configure logger
    configure_logger(verbose)
    logger = logging.getLogger(__name__)
    logger.info(f'Converting model, target_data_format: {target_data_format}')

    if inputs_to_transpose is None:
        inputs_to_transpose = []
    model_converter = ModelConverter(model, target_data_format, inputs_to_transpose)
    converted_model = model_converter.convert_model()
    return converted_model

