import abc
from typing import List

from rich.console import Console
from rich.table import Table
from yaspin import yaspin


class BaseObservable(abc.ABC):
    def __init__(self, client=None, spinner_load_type=""):
        self.client = client
        self.console = Console()
        self.spinner = yaspin(text=f"Loading {spinner_load_type}...", color="yellow")

    @abc.abstractmethod
    def get(self, is_global: bool):
        """
        Get the status of the resources

        Parameters
        ----------
        is_global:
            If True, returns status of resources for everyone in the team
        """

    @abc.abstractmethod
    def follow(self, is_global: bool):
        """
        Parameters
        ----------
        is_global:
            If True, returns status of resources for everyone in the team
        """

    @staticmethod
    def create_table(columns: List[str]) -> Table:
        return create_table(columns)


def create_table(columns: List[str]) -> Table:
    table = Table(show_header=True, header_style="bold green")
    table.add_column(columns[0], style='dim')
    for column in columns[1:]:
        table.add_column(column, justify='right')
    return table
