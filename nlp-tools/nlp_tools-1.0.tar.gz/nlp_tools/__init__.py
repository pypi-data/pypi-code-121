import os
from typing import Dict,Any
os.environ['TF_KERAS'] = '1'
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'

custom_objects: Dict[str, Any] = {}

from nlp_tools.__version__ import __version__
from nlp_tools.macros import config
from nlp_tools import layers
from nlp_tools import corpus
from nlp_tools import embeddings
from nlp_tools import macros
from nlp_tools import processors
from nlp_tools import tasks
from nlp_tools import utils
#from nlp_tools import callbacks

custom_objects = layers.resigter_custom_layers(custom_objects)
from tensorflow import keras
keras.utils.get_custom_objects().update(custom_objects)