from abc import ABCMeta, abstractmethod
from typing import Tuple, List
from v5rpc.types import EventArguments, Field


class IStrategy(metaclass=ABCMeta):
    @abstractmethod
    def on_event(self, event_type: int, args: EventArguments) -> None:
        """
        :param event_type:
        :param args:
        :return:
        """

    @abstractmethod
    def get_team_info(self, server_version: int) -> str:
        """
        :param server_version:
        :return:
        """

    @abstractmethod
    def get_instruction(self, field: Field) -> Tuple[List[Tuple[float, float]], int]:
        """
        :param field:
        :return:
        """

    @abstractmethod
    def get_placement(self, field: Field) -> List[Tuple[float, float, float]]:
        """
        :param field:
        :return:
        """
