# ENDPOINTS
PUSH_SUPPORT_FILES_ENDPOINT = 'https://wpxkueck1a.execute-api.us-west-2.amazonaws.com/Prod/customer_download'
NAME_RESERVATION_ENDPOINT = 'https://wpxkueck1a.execute-api.us-west-2.amazonaws.com/Prod/registered_vendor_name'
PRESIGNED_REQUEST_ENDPOINT = 'https://wpxkueck1a.execute-api.us-west-2.amazonaws.com/Prod/hello'
STATUS_UPDATE_ENDPOINT_PREFIX = 'https://1quz3qvhsi.execute-api.us-west-2.amazonaws.com/Prod/push-model'
INFERENCE_ENDPOINT_PREFIX = 'https://api.tiyaro.ai/v1/ent'

# SHARED CONSTANTS
TIYARO_API_KEY = 'TIYARO_API_KEY'
TIYARO_JOB_DESCRIPTOR = 'GIT_PYTORCH_SNAPSHOT'
TIYARO_MODEL_TYPE = 'GIT_PASSTHROUGH'
MODEL_VERSION = '1.0'

VERBOSE_HELP = f'Display more logs'

# INIT CONSTANTS
TIYARO_HANDLER_DIR = './tiyaro_handler'
ARTIFACTS_DOWNLOAD_DIR = f'{TIYARO_HANDLER_DIR}/artifacts'
ARTIFACTS_FILE_NAME = 'tiyaro_handler_templates.tgz'
ARTIFACTS_FILES_DIR = 'staging/tiyaro_handler/'
MODEL_HANDLER = 'model_handler'
HANDLER_MODEL_MANIFEST_FILE = f'{TIYARO_HANDLER_DIR}/model_manifest.yml'
HANDLER_MODEL_MODULE_FILE = f'{TIYARO_HANDLER_DIR}/__init__.py'
HANDLER_MODEL_MODEL_HANDLER_FILE = f'{TIYARO_HANDLER_DIR}/{MODEL_HANDLER}.py'
HANDLER_MODEL_CUSTOM_HANDLER_FILE = f'{TIYARO_HANDLER_DIR}/{MODEL_HANDLER}_custom.py'
HANDLER_MODEL_IMAGE_CLASSIFICATION_HANDLER_FILE = f'{TIYARO_HANDLER_DIR}/{MODEL_HANDLER}_image_classification.py'
HANDLER_MODEL_TEXT_CLASSIFICATION_HANDLER_FILE = f'{TIYARO_HANDLER_DIR}/{MODEL_HANDLER}_text_classification.py'
HANDLER_MODEL_CLASS_TEMPLATES_PATTERN = f'{TIYARO_HANDLER_DIR}/{MODEL_HANDLER}_*.py'
HANDLER_MODEL_MODEL_TEST_FILE = 'tiyaro_handler_test.py'
TIYARO_INTERNAL_DIR = f'{TIYARO_HANDLER_DIR}/.tiyaro'
TIYARO_INTERNAL_STATE_FILE = f'{TIYARO_INTERNAL_DIR}/cli_state.json'
TIYARO_INTERNAL_TEST_STATE_FILE = f'{TIYARO_INTERNAL_DIR}/test_state.json'

CLASS_CUSTOM = 'custom'
CLASS_IMAGE_CLASSIFICATION = 'image-classification'
CLASS_TEXT_CLASSIFICATION = 'text-classification'

class_handler_map = {
    CLASS_IMAGE_CLASSIFICATION: HANDLER_MODEL_IMAGE_CLASSIFICATION_HANDLER_FILE,
    CLASS_TEXT_CLASSIFICATION: HANDLER_MODEL_TEXT_CLASSIFICATION_HANDLER_FILE,
    CLASS_CUSTOM: HANDLER_MODEL_CUSTOM_HANDLER_FILE
}

INIT_HELP = f'Forcefully recreates {TIYARO_HANDLER_DIR}, {HANDLER_MODEL_MODEL_TEST_FILE} templates'


# PUSH CONSTANTS
UPLOAD_ARTIFACT_DIR = './build'
GIT_SNAPSHOT_FILE_NAME = 'git_snapshot.tgz'
JSON_MANIFEST_FILE_NAME = 'manifest.json'
FILE_TO_UPLOAD = '/tmp/build.tgz'
STATUS_PAGE_URL = 'https://console.tiyaro.ai/modelstudio-publish'

CLEAN_HELP = f'Forcefully clean {TIYARO_HANDLER_DIR}, {HANDLER_MODEL_MODEL_TEST_FILE} templates'

# TEST CONSTANTS
TIYARO_TEST_VENV_PATH = './.tiyaro_test_venv'
KEYWORD_FROM_CONFIG = 'from-config'

# keys in model_handler.yml
C_PRETRAINED_FILE_OR_URL = 'pretrained_model_url'
C_MODEL_FILE_PATH = 'model_file_path'
C_REQUIREMENTS_FILE = 'reqirements_file_path'

C_MODEL_TYPE = 'model_type'
C_MODEL_CLASS = 'model_class'
C_MODEL_FRAMEWORK = 'model_framework'

# keys in test_state.json
C_TEST_INPUT = 'test_input'
C_TEST_OUTPUT = 'test_output'
C_TEST_USER_CONFIRMED = 'test_user_confirmed_output'


CMD_TIYARO_FORCE_CLEAN = 'tiyaro clean -f'
