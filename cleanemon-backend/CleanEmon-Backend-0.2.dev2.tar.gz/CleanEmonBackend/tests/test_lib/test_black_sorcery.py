from CleanEmonBackend import NILM_INFERENCE_APIS_DIR
from CleanEmonBackend.lib.black_sorcery import nilm_path_fix


def test_nilm_path_fix():
    import os
    import sys

    with nilm_path_fix():
        assert os.getcwd() == NILM_INFERENCE_APIS_DIR
        assert NILM_INFERENCE_APIS_DIR in sys.path
