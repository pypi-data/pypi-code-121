import logging
from pathlib import Path
from shutil import move
from typing import Any, List, NamedTuple

from .util import log_utf8_safe


class Command(NamedTuple):
    src: Path = None
    dest: Path = None
    info: List[Any] = []

    @property
    def source(self) -> str:
        return str(self.src.resolve())

    @property
    def destination(self) -> str:
        return str(self.dest.resolve())

    def execute(self, force: bool) -> None:
        if force:
            self.do_execute()
        self.print()

    def print(self) -> None:
        raise NotImplementedError()

    def do_execute(self) -> None:
        raise NotImplementedError()


class Nothing(Command):
    def do_execute(self) -> None:
        pass

    def print(self) -> None:
        pass


class Move(Command):
    def do_execute(self) -> None:
        try:
            move(self.source, self.destination)
        except FileNotFoundError:
            log_utf8_safe('FAIL:', self.source, '->', self.destination)

    def print(self) -> None:
        logging.info('mv %s %s # %s', self.source, self.destination, self.info)


class Relink(Command):
    @property
    def new_symlink(self) -> Path:
        return self.src.parent.joinpath(self.dest.name)

    def do_execute(self) -> None:
        self.src.unlink()
        self.new_symlink.symlink_to(self.dest)

    def print(self) -> None:
        logging.info('rm -f %s', self.source)
        logging.info('ln -s %s %s', self.destination, str(self.new_symlink))


Commands = List[Command]
