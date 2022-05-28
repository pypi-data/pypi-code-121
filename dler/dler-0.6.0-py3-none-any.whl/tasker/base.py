import os
import shutil
from typing import Dict, Any
from urllib.parse import urlparse, ParseResult
from multitasker import MultiTasker

from dler import constants
from .exceptions import FileExistsException

class BaseConfig:
    task_type: str
    download_dir: str = constants.ENV_DOWNLOAD_DIR or constants.DOWNLOAD_DIR
    cache_dir: str = constants.CACHE_DIR


class BaseTasker(MultiTasker):
    url: str
    filename: str
    filetype: str
    urlparse: ParseResult

    class Config(BaseConfig):
        pass

    @property
    def download_dir(self) -> str:
        """doc"""
        return self.Config.download_dir

    @property
    def filepath(self) -> str:
        """doc"""
        return os.path.join(self.download_dir, self.filename)

    @property
    def cache_dir(self) -> str:
        """doc"""
        return os.path.join(self.Config.cache_dir, f"{self.filename}")

    def __init__(self,
            url: str, filename: str = None, config: Dict[str, Any] = None
    ) -> None:
        self.url = url
        self.urlparse = urlparse(url)
        self.filename = filename or os.path.basename(
            self.urlparse.path.strip('/'))

        filenames = self.filename.split('.')
        self.filetype = filenames[1] if len(filenames) > 1 else None

        if config:
            for key, value in config.items():
                setattr(self.Config, key, value)

        self._init()

    def _init(self):
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def check_file_exists(self):
        if os.path.exists(self.filepath):
            raise FileExistsException()

    def before_build(self):
        pass

    def after_run(self):
        pass

    def before_run(self):
        pass

    def clear(self):
        shutil.rmtree(self.cache_dir)
