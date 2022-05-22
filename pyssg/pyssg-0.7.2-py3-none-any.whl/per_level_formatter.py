from logging import Formatter, DEBUG, INFO, WARNING, ERROR, CRITICAL


class PerLevelFormatter(Formatter):
    # colors for the terminal in ansi
    __YELLOW: str = "\x1b[33m"
    __RED: str = "\x1b[31m"
    __BOLD_RED: str = "\x1b[31;1m"
    __RESET: str = "\x1b[0m"

    __DATE_FMT: str = '%Y-%m-%d %H:%M:%S'
    __COMMON_FMT: str = '[%(levelname)s] [%(module)s:%(funcName)s:%(lineno)d]: %(message)s'
    __FORMATS: dict[int, str] = {
        DEBUG: __COMMON_FMT,
        INFO: '%(message)s',
        WARNING: f'{__YELLOW}{__COMMON_FMT}{__RESET}',
        ERROR: f'{__RED}{__COMMON_FMT}{__RESET}',
        CRITICAL: f'{__BOLD_RED}{__COMMON_FMT}{__RESET}'
    }


    def format(self, record: str) -> str:
        fmt: str = self.__FORMATS.get(record.levelno)
        formatter: Formatter = Formatter(
            fmt=fmt, datefmt=self.__DATE_FMT, style='%')

        return formatter.format(record)
