from shlex import split as shlex_split
from threading import Thread
from typing import Optional, Dict

from .exceptions import DuplicatedCommand, CommandInterfaceExists, CommandExecutionError


def _extract_args(string):
    return shlex_split(string)


class CommandInterface:
    __LOCK = False

    def __init__(self):
        if CommandInterface.__LOCK:
            raise CommandInterfaceExists('Only one CommandInterface is allowed')
        CommandInterface.__LOCK = True

        self._input_thread = Thread(name='CommandInterface Input Thread', target=self._input_loop, daemon=True)
        self._input: Optional[str] = None
        self._stopped = False

        self._getting_input: bool = False
        self._commands: Dict[str, Command] = {}

    def __del__(self):
        CommandInterface.__LOCK = False

    def _input_loop(self):
        while not self._stopped:
            self._input = input()
            self._analyze_input()

    def _analyze_input(self):
        if self._getting_input:
            return

        split = self._input.split(" ", 1)
        split.append("")
        if split[0] in self._commands.keys():
            command = self._commands.get(split[0])
            if command.thread:
                Thread(name=f'CommandInterface Command "{split[0]}"', target=command.execute, daemon=command.daemon, kwargs={'args': split[1]}).start()

        self._input = None

    def get_input(self, prompt=None):
        self._getting_input = True
        if prompt is not None:
            print(prompt, end='')

        while self._input is None:
            pass

        value = self._input
        self._input = None
        return value

    def command(self, name, thread=True, daemon=True):
        if name in self._commands.keys():
            raise DuplicatedCommand(f'Command "{name}" already exists in the CommandInterface')

        def decorator(func):
            self._commands[name] = Command(name, thread, daemon, func)
            return self._commands[name]

        return decorator

    def start(self):
        self._input_thread.start()

    def stop(self):
        self._stopped = True

    def is_alive(self):
        return self._input_thread.is_alive()


class Command:
    def __init__(self, name, thread, daemon, func):
        self.name = name
        self.thread = thread
        self.daemon = daemon
        self.func = func

    def execute(self, args):
        try:
            args = _extract_args(args)
            self.func(*args)
        except Exception as exception:
            raise CommandExecutionError('An unexpected error occurred') from exception
