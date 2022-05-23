import logging
import os
import re
from os import mkdir, path
from pathlib import Path


DATA_PATH=os.getenv('KOLIBRI_DATA_PATH')

if DATA_PATH is None:
    DATA_PATH = os.path.join(str(Path.home()), '.kolibri')
    os.environ['KOLIBRI_DATA_PATH']=DATA_PATH
GITHUB_TOKEN="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"
GITHUB_REPO_NAME="mbenhaddou/kolibri-data"
MODEL_CARD_NAME = "model_card.json"

Path(DATA_PATH).mkdir(exist_ok=True, parents=True)


# [entity_text](entity_type(:entity_synonym)?)
ent_regex = re.compile(r'\[(?P<entity_text>[^\]]+)'
                       r'\]\((?P<entity>[^:)]*?)'
                       r'(?:\:(?P<text>[^)]+))?\)')


os.environ['Kolibri_DOWNLOAD_URL']="https://raw.githubusercontent.com/mbenhaddou/kolibri-data/main/index.json"
RELATIVE_ERROR = 10000
DEFAULT_SERVER_PORT = 5005
DEFAULT_SEED=4231
EMBEDDING_SIZE = 100
WORD2VEC_WORKERS = 4
MIN_WORD_COUNT = 5
WORD2VEC_CONTEXT = 5
TARGET_RANKING_LENGTH = 10
LOGS_DIR = path.join(DATA_PATH, 'logs')
LOG_NAME = 'kolibri'
LOG_FILE = path.join(LOGS_DIR, LOG_NAME + '.log')
LOG_LEVEL = logging.DEBUG
INCOMPLETE_SUFFIX = '.incomplete'

MINIMUM_COMPATIBLE_VERSION = "0.0.1"

DEFAULT_NLU_FALLBACK_THRESHOLD = 0.0

DEFAULT_CORE_FALLBACK_THRESHOLD = 0.0

DEFAULT_REQUEST_TIMEOUT = 60 * 5  # 5 minutes

DEFAULT_SERVER_FORMAT = "http://localhost:{}"

DEFAULT_SERVER_URL = DEFAULT_SERVER_FORMAT.format(DEFAULT_SERVER_PORT)


DOCUMENT_TEXT_MAX_LENGTH = 255

DOCUMENT_LABEL_MAX_LENGTH = 32

# The maximum length_train of characters that the name of a tag can contain
TAG_NAME_MAX_LENGTH = 50

DIRS = [DATA_PATH, LOGS_DIR]





