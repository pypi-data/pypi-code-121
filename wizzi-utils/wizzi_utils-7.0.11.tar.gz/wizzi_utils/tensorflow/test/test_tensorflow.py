from wizzi_utils.tensorflow import tensorflow_tools as tft
from wizzi_utils.misc import misc_tools as mt


def get_tensorflow_version_test():
    mt.get_function_name(ack=True, tabs=0)
    tft.get_tensorflow_version(ack=True)
    return


def gpu_detected_test():
    mt.get_function_name(ack=True, tabs=0)
    print('\tgpu available ? {}'.format(tft.gpu_detected()))
    return


def test_all():
    print('{}{}:'.format('-' * 5, mt.get_base_file_and_function_name()))
    get_tensorflow_version_test()
    gpu_detected_test()
    print('{}'.format('-' * 20))
    return
