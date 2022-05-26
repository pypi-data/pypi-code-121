from typing import List, TYPE_CHECKING

import api
import utils

if TYPE_CHECKING:
    from models.public_notice import Corporation


FILE_NAME = 'listed_corps'
listed_corps: List['Corporation']

try:
    listed_corps: List['Corporation'] = utils.read_json_by_file_path(FILE_NAME)
except:
    listed_corps: List['Corporation'] = api.fetch_all_listed_corp()
    utils.save_json_as_file(listed_corps, FILE_NAME)

# 디렉토리를 확인하세요
