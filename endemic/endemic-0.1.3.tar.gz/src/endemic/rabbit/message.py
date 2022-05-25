from datetime import datetime
from .constant import *


class Message:
    def __init__(self):
        self.__link = None
        self.__link = None

    def default(self, project_flow: list, data: list) -> dict:
        return {
            PROJECT_FLOW: project_flow,
            MESSAGE_CREATED: datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000000'),
            LINK: self.__link,
            DATA: data if data else []
        }

    @property
    def link(self):
        return self.__link

    @link.setter
    def link(self, value: str):
        self.__link = value
