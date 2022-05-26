
import inspect
from modulefinder import Module
import sys
from typing import Optional
from pydantic import BaseModel

FOLDER_MAGIC_STR = '__folder__'
FOLDER_MAGIC_TITLE_STR = '__folder_title__'
FOLDER_MAGIC_UID_STR = '__folder_uid__'

class Folder(BaseModel):
    uid: Optional[str]
    title: Optional[str]

    def __init__(self, **data):
        super().__init__(**data)
        caller = inspect.currentframe().f_back
        caller_module = sys.modules[caller.f_globals['__name__']]
        setattr(caller_module, FOLDER_MAGIC_STR, self)
        Folder.set_title(caller_module, self.title)
        Folder.set_uid(caller_module, self.uid)

    @classmethod
    def get_title(cls, folder_module: Module) -> str:
        return folder_module.__dict__.get(FOLDER_MAGIC_TITLE_STR)

    @classmethod
    def set_title(cls, folder_module: Module, title: str) -> str:
        setattr(folder_module, FOLDER_MAGIC_TITLE_STR, title)

    @classmethod
    def get_uid(cls, folder_module: Module) -> str:
        return folder_module.__dict__.get(FOLDER_MAGIC_UID_STR)

    @classmethod
    def set_uid(cls, folder_module: Module, title: str) -> str:
        setattr(folder_module, FOLDER_MAGIC_UID_STR, title)
