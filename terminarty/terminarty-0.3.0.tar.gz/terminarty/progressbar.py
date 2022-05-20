from colorama import Fore, Style

from .terminal import Terminal


class ProgressBar:
    def __init__(self, total: [int, float]) -> None:
        self.total = total
        self.current = 0
        self.procentage = 0
        print(self, end='')

    def __str__(self) -> str:
        s = (
            '\r'
            f'{Fore.GREEN}{"━" * int(self.procentage / 4)}'
            f'{Fore.RED}{"─" * (25 - int(self.procentage / 4))}'
            f'{Fore.CYAN} {self.current}{Fore.BLUE}/{Fore.CYAN}{self.total} '
            f'{Fore.YELLOW}{self.procentage}%'
            f'{Style.RESET_ALL}'
        )
        if self.current == self.total:
            Terminal._updating_line = ''
            return s + '\n'
        else:
            Terminal._updating_line = s
            return s

    def __iadd__(self, value: [int, float]) -> 'ProgressBar':
        self.update(self.current + value)
        return self

    def __isub__(self, value: [int, float]) -> 'ProgressBar':
        self.update(self.current - value)
        return self

    def update(self, current: [int, float]) -> None:
        if current > self.total:
            self.current = self.total
        else:
            self.current = current
        self.procentage = round(current * 100 / self.total, 2)
        print(self, end='')
