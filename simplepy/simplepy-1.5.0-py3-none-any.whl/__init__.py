import os

from simplepy.config import env
from simplepy.logger import Logger

logger = Logger()
LIB_PATH = os.path.dirname(__file__)
ROOT_PATH = os.path.dirname(LIB_PATH)


def init_db(path=False):
    if not os.path.isfile(path):
        logger.warning('请传递正确的环境变量路径')
    env.read_env(path)
    from simplepy import config
