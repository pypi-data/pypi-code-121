import logging

handler = logging.StreamHandler()
msg_format = '%(levelname)-8s %(message)s'
formatter = logging.Formatter(msg_format)
handler.setFormatter(formatter)

root_logger = logging.getLogger()
root_logger.addHandler(handler)
root_logger.setLevel(logging.INFO)


def get_logger() -> logging.Logger:
    return logging.getLogger()


def set_level(level: str) -> None:
    root_logger.setLevel(level)
