from typing import List

from .commit import Commit


class Repository:
    def __init__(self, name: str, owner: str, commits: List[Commit]) -> None:
        self.__name = name
        self.__owner = owner
        self.__commits = commits

    @property
    def name(self) -> str:
        return self.__name

    @property
    def owner(self) -> str:
        return self.__owner

    @property
    def commits(self) -> List[Commit]:
        return self.__commits.copy()
