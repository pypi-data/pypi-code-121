import functools
import json
import sys
from pathlib import Path
from typing import Any, Union

import stackprinter
from loguru import logger
from pydantic import BaseModel


def record_formatter(record):
    """for json formatting"""
    simplified = {
        "timestamp": record["time"].timestamp(),
        "elapsed": str(record["elapsed"]),
        "level": record["level"].name,
        "name_function_line": f"{record['name']}_{record['function']}_{record['line']}",
        "module": record["module"],
        "message": record["message"],
        "exception": "",
    }
    if record["exception"] is not None:
        simplified["exception"] = stackprinter.format(record["exception"])

    return json.dumps(simplified)


def formatter(record):
    """for json formatting"""
    record["extra"]["serialized"] = record_formatter(record)
    return "{extra[serialized]}\n"


class LoguruHandler(BaseModel):
    logger: Any
    format_md: str = "* {time:YYYY-MM-DD at HH:mm:ss} | elapsed:{elapsed} | {level} | module:{module} | {name}:{function}:{line} | {message}"
    format_stderr: str = "* <green>{time:YYYY-MM-DD at HH:mm:ss}</green>| elapsed:{elapsed} | module:{module} | <red>{level}</red> | <cyan>{name}:{function}:{line}</cyan> | {message}"

    class Config:
        arbitrary_types_allowed = True

    def logger_wraps(self, *, is_entry=True, is_exit=True, level="INFO"):
        def wrapper(func):
            name = func.__name__

            @functools.wraps(func)
            def wrapped(*args, **kwargs):
                logger_ = self.logger.opt(depth=1)
                if is_entry:
                    logger_.log(
                        level, f"Entering '{name}' (args={args}, kwargs={kwargs})"
                    )
                result = func(*args, **kwargs)
                if is_exit:
                    logger_.log(level, f"Exiting '{name}' (result={result})")
                return result

            return wrapped

        return wrapper

    def __init__(self, logger: Any, **data: Any) -> None:
        super().__init__(**data)
        self.logger = logger
        self.logger.remove()

    def add_logger(
        self,
        *,
        filename: Union[str, Path] = "stderr",
        level: str = "INFO",  # "INFO" | "WARNING"
    ):
        # TODO: validate level
        # TODO: validate filename
        # TODO: level-based coloring (call out warning)
        if filename == "stderr":
            self.logger.add(
                sys.stderr,
                colorize=True,
                format=self.format_stderr,
                level=level,
                enqueue=True,
            )
        else:
            ext = Path(filename).suffix
            if ext == ".md":
                self.logger.add(
                    filename,
                    format=self.format_md,
                    enqueue=True,
                    backtrace=True,
                    diagnose=True,
                    rotation="10 MB",
                    # retention="30 days",
                )
            elif ext == ".json":
                self.logger.add(
                    filename,
                    format=formatter,
                    serialize=True,
                    enqueue=True,
                    backtrace=True,
                    diagnose=True,
                    rotation="10 MB",
                    # retention="30 days",
                )
            else:
                raise ValueError(
                    f"Only filenames ending with .md or .json allowed. Received{filename}"
                )

        filename = Path(filename)


# TODO: Create EXCPTION level (and formatter for it)
# logger.add(
#     sys.stdout,
#     colorize=True,
#     format=format_stdout",
#     level="EXCEPTION",
#     enqueue=True,
#     backtrace=True,
#     diagnose=True,
# )

# TODO: Create different formatters for stdout, md_logfile, json_logfiles
# class Formatter:
#     """for stdout formatting"""

#     def __init__(self):
#         self.padding = 0
#         self.fmt = "{time} | {level: <8} | {name}:{function}:{line}{extra[padding]} | {message}\n{exception}"

#     def format(self, record):
#         length = len("{name}:{function}:{line}".format(**record))
#         self.padding = max(self.padding, length)
#         record["extra"]["padding"] = " " * (self.padding - length)
#         ## if record["exception"] is not None:
#         ##     record["extra"]["stack"] = stackprinter.format(record["exception"])
#         ##     format_ += "{extra[stack]}\n"
#         return self.fmt


# formatter = Formatter()
# then use formatter.format

# TODO: https://loguru.readthedocs.io/en/stable/resources/recipes.html#manipulating-newline-terminator-to-write-multiple-logs-on-the-same-line
# TODO: https://loguru.readthedocs.io/en/stable/resources/recipes.html#interoperability-with-tqdm-iterations
# TODO: https://loguru.readthedocs.io/en/stable/api/type_hints.html
