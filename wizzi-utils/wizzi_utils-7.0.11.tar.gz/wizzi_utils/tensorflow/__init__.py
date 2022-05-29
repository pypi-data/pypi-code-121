"""
:requires: tensorflow
    gpu:
        cuda>=10: pip install tensorflow-gpu
        cuda==9.1: pip install tensorflow-gpu==1.12
        for more versions:
            https://stackoverflow.com/questions/50622525/which-tensorflow-and-cuda-version-combinations-are-compatible
    cpu: pip install tensorflow
"""
try:
    from wizzi_utils.tensorflow.tensorflow_tools import *
except ModuleNotFoundError as e:
    pass

from wizzi_utils.tensorflow import test
