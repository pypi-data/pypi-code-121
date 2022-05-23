import importlib

from packaging import version
import tensorflow as tf
#from kolibri.backend.tensorflow.tasks.audio import *
#from kolibri.backend.tensorflow.tasks.text import *
import sys
from kolibri.logger import get_logger
logger = get_logger(__name__)


if sys.version_info < (3, 8):
    import importlib_metadata
else:
    import importlib.metadata as importlib_metadata

tf.compat.v1.logging.set_verbosity(tf.compat.v1.logging.ERROR)
custom_objects = tf.keras.utils.get_custom_objects()


def custom_object_scope():
    return tf.keras.utils.custom_object_scope(custom_objects)



is_torch_available = importlib.util.find_spec("torch") is not None
if is_torch_available:
    try:
        _torch_version = importlib_metadata.version("torch")
        logger.info(f"PyTorch version {_torch_version} available.")
    except importlib_metadata.PackageNotFoundError:
        is_torch_available = False
else:
    logger.info("Disabling PyTorch because USE_TF is set")
    is_torch_available = False




is_tf_available = importlib.util.find_spec("tensorflow") is not None
_tf_version=""

if is_tf_available:
    # For the metadata, we have to look for both tensorflow and tensorflow-cpu
    try:
        _tf_version = importlib_metadata.version("tensorflow")
    except importlib_metadata.PackageNotFoundError:
        try:
            _tf_version = importlib_metadata.version("tensorflow-cpu")
        except importlib_metadata.PackageNotFoundError:
            try:
                _tf_version = importlib_metadata.version("tensorflow-gpu")
            except importlib_metadata.PackageNotFoundError:
                try:
                    _tf_version = importlib_metadata.version("tf-nightly")
                except importlib_metadata.PackageNotFoundError:
                    try:
                        _tf_version = importlib_metadata.version("tf-nightly-cpu")
                    except importlib_metadata.PackageNotFoundError:
                        try:
                            _tf_version = importlib_metadata.version("tf-nightly-gpu")
                        except importlib_metadata.PackageNotFoundError:
                            _tf_version = None
                            is_tf_available = False
if is_tf_available:
    if version.parse(_tf_version) < version.parse("2"):
        logger.info(f"TensorFlow found but with version {_tf_version}. Transformers requires version 2 minimum.")
        is_tf_available = False
    else:
        logger.info(f"TensorFlow version {_tf_version} available.")
else:
    logger.info("Disabling Tensorflow because USE_TORCH is set")
    is_tf_available = False