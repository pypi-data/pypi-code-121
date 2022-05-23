import logging

# import os


def get_logger(name: str, log_path: str = "log") -> logging.Logger:
    logger = logging.getLogger(name)
    # if not os.path.exists(log_path):
    #     os.makedirs(log_path)
    # handler = logging.FileHandler(f"{logs_path}/{name}.log", mode="w")
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    return logger
