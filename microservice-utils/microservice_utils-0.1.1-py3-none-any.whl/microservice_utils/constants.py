import logging

LOG_FORMATTER = logging.Formatter(
    fmt="[%(asctime)s] [%(levelname)s] %(message)s", datefmt="%Y-%m-%d %I:%M:%S%z"
)
