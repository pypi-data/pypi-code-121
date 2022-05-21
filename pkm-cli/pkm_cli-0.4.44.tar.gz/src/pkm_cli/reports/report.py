from abc import abstractmethod, ABC

from pkm_cli.display.display import Display


class Report(ABC):

    @abstractmethod
    def display(self, dumb: bool = Display.is_dumb()):
        ...
