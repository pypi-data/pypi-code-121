import threading
import time
from typing import Optional

from colorama import Fore, Style

from . import Terminal


class Waiting:
    def __init__(self, doing: str, delay: Optional[float] = 0.3) -> None:
        self.doing = doing.strip().rstrip('...')
        self.delay = delay
        self._running = True
        self._thread = threading.Thread(target=self._loop, daemon=True)

    def __enter__(self) -> 'Waiting':
        self.start()
        return self

    def __exit__(self, exc_type, exc_value, traceback) -> None:
        self._stop()
        if exc_type is not None:
            s = f'\r{self.doing}... {Fore.RED}ERROR{Style.RESET_ALL}'
            Terminal._updating_line = s
            print(s)
        else:
            s = f'\r{self.doing}... {Fore.GREEN}DONE{Style.RESET_ALL}'
            Terminal._updating_line = s
            print(s)

    def _loop(self):
        dots = 1
        while self._running:
            s = f'\r{self.doing}{dots * "."}{" " * (3 - dots)}{Style.RESET_ALL}'
            Terminal._updating_line = s
            print(s, end='')
            dots += 1 if dots < 3 else -2
            time.sleep(self.delay)

    def _stop(self) -> None:
        Terminal._updating_line = ''
        self._running = False
        self._thread.join()

    def start(self) -> None:
        self._running = True
        self._thread.start()

    def done(self) -> None:
        self._stop()
        print(f'\r{self.doing}... {Fore.GREEN}DONE{Style.RESET_ALL}')

    def error(self) -> None:
        self._stop()
        print(f'\r{self.doing}... {Fore.RED}ERROR{Style.RESET_ALL}')
