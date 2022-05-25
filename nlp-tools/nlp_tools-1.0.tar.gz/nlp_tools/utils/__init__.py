import warnings
import tensorflow as tf
from typing import TYPE_CHECKING,Union
from tensorflow.keras.utils import CustomObjectScope

from nlp_tools import  custom_objects
from nlp_tools.utils.serialize import load_data_object
from nlp_tools.utils.data import get_list_subset
from nlp_tools.utils.data import unison_shuffled_copies
from nlp_tools.utils.multi_label import MultiLabelBinarizer
import random
import os
import numpy as np


def custom_object_scope() -> CustomObjectScope:
    return tf.keras.utils.custom_object_scope(custom_objects)


def seed_tensorflow(seed=42):
    random.seed(seed)
    os.environ['PYTHONHASHSEED'] = str(seed)
    np.random.seed(seed)
    tf.random.set_seed(seed)
    os.environ['TF_DETERMINISTIC_OPS'] = '1' # pip install tensorflow-determinism
