import os
import pkgutil
import sys
from typing import Type

from dimtim.helpers.management import CommandBase
from dimtim.utils import importing, terminal


class CommandRunner:
    def __init__(self, runner_path: str, path: str):
        self.runner_path = os.path.abspath(runner_path)
        self.path = path
        self.os_path = path.replace('.', '/').rstrip('/')

    def collect_tasks(self) -> list[tuple[str, Type[CommandBase]]]:
        result = []
        for _, name, is_pkg in pkgutil.iter_modules([self.os_path]):
            _module = importing.safe_import(f'{self.path}.{name}', False)
            if not is_pkg and (cls := getattr(_module, 'Command', None)):
                result.append((name, cls))
        return result

    def available_tasks_string(self) -> str:
        tasks = self.collect_tasks()
        max_name_length = max(len(name) for name, _ in tasks)
        result = []
        for name, command in tasks:
            task_name = terminal.colorize(name, ['bold'], fg='green')
            help_text = command.help
            result.append(f'    + {task_name} %s {help_text}' % ('-' * (max_name_length - len(name) + 1)))
        return 'Available tasks: \n%s\n' % '\n'.join(result)

    def run(self):
        if len(sys.argv) > 1:
            task, *args = sys.argv[1:]

            if module := importing.safe_import(f'{self.path}.{task}', True):
                if hasattr(module, 'Command') and issubclass(module.Command, CommandBase):
                    module.Command(self.runner_path).run(args)
                else:
                    sys.stderr.write(f'Task "{task}" is broken.\n')
                    exit(-1)
            else:
                sys.stderr.write(f'Task "{task}" not found.\n{self.available_tasks_string()}')
                exit(-1)
        else:
            sys.stderr.write(self.available_tasks_string())
