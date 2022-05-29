from wizzi_utils import misc_tools as mt  # misc tools
import os
import warnings

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'  # removes tf informative messages
warnings.simplefilter(action='ignore', category=FutureWarning)  # remove tf future warnings
# noinspection PyPackageRequirements,PyUnresolvedReferences
import tensorflow as tf  # noqa E402


def get_tensorflow_version(ack: bool = False, tabs: int = 1) -> str:
    """
    :param ack:
    :param tabs:
    :return:
    see get_tensorflow_version_test()
    """
    # print(tf.__version__)
    # print(tf.VERSION)
    # print(tf.version.VERSION)
    # noinspection PyUnresolvedReferences
    string = mt.add_color('{}* TensorFlow Version {}'.format(tabs * '\t', tf.__version__), ops=mt.SUCCESS_C)
    string += mt.add_color(' - GPU detected ? ', ops=mt.SUCCESS_C)
    if gpu_detected():
        string += mt.add_color('True', ops=mt.SUCCESS_C2)
    else:
        string += mt.add_color('False', ops=mt.FAIL_C2)
    if ack:
        print(string)
    return string


def gpu_detected() -> bool:
    """
    :return:
    """
    gpu_on = False
    try:  # version >= 2
        # noinspection PyUnresolvedReferences
        if len(tf.config.list_physical_devices('GPU')) >= 1:
            gpu_on = True
    except AttributeError:
        # noinspection PyUnresolvedReferences
        if 'GPU' in tf.test.gpu_device_name():
            gpu_on = True
    return gpu_on
