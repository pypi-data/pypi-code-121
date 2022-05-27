import os

from ..common.constants import *
from ..common.utils import failed

def validate_handler_exists():
    if (not os.path.exists(HANDLER_MODEL_MANIFEST_FILE)
            or not os.path.exists(HANDLER_MODEL_MODULE_FILE)
            or not os.path.exists(HANDLER_MODEL_MODEL_HANDLER_FILE)
            ):
        failed(
            f'Missing mandatory files in {TIYARO_HANDLER_DIR} directory.  Initialize using tiyaro init')
        exit(-1)


def validate_model_manifest_file_exists():
    if (not os.path.exists(HANDLER_MODEL_MANIFEST_FILE)):
        failed(
            f'Missing mandatory model handler file: {HANDLER_MODEL_MANIFEST_FILE}.  Initialize using tiyaro init')
        exit(-1)


def validate_handler_test_file_exists():
    if (not os.path.exists(HANDLER_MODEL_MODEL_TEST_FILE)):
        failed(
            f'Missing mandatory handler test file: {HANDLER_MODEL_MODEL_TEST_FILE}.  Initialize using tiyaro init')
        exit(-1)
