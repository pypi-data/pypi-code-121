from wizzi_utils import misc_tools as mt  # misc tools
# noinspection PyPackageRequirements
import tflite_runtime


# from tflite_runtime.interpreter import Interpreter

# try:
#     # noinspection PyUnresolvedReferences
#     interpreter_found = tflite_runtime.interpreter.Interpreter
#     print('success using tflite_runtime.interpreter.Interpreter')
# except AttributeError:
#     # print('failure using tflite_runtime.interpreter.Interpreter')
#     try:
#         # noinspection PyPackageRequirements,PyUnresolvedReferences
#         import tensorflow as tf
#
#         interpreter_found = tf.lite.Interpreter
#         print('success using tf.lite.Interpreter')
#     except (ImportError, AttributeError):
#         pass
#         print('failure using tf.lite.Interpreter')


def get_tflite_version(ack: bool = False, tabs: int = 1) -> str:
    """
    :param ack:
    :param tabs:
    :return:
    see get_tflite_version_test()
    """
    string = mt.add_color('{}* TFLite Version {}'.format(tabs * '\t', tflite_runtime.__version__), ops=mt.SUCCESS_C)
    # string += mt.add_color(' - GPU detected ? ', op1=mt.SUCCESS_C)
    # if gpu_detected():
    #     string += mt.add_color('True', op1=mt.SUCCESS_C2[0], extra_ops=mt.SUCCESS_C2[1])
    # else:
    #     string += mt.add_color('False', op1=mt.FAIL_C2[0], extra_ops=mt.FAIL_C2[1])
    if ack:
        print(string)
    return string


def gpu_detected() -> bool:
    """
    TODO future
    :return
    """
    return False
