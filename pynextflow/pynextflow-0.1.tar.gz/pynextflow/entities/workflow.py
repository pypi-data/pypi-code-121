from typing import List, Tuple

from pynextflow.entities.process import Process


class Workflow:
    name: str
    processes: List[Process]
    args: Tuple
    body: str

    def __init__(self, name: str, processes: List[Process], body: str, args, func):
        self.name = name
        self.processes = processes
        self.args = args
        self.body = body
        self.func = func