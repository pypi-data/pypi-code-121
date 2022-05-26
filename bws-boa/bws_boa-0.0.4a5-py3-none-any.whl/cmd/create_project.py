import logging
from .base import create_project
logger = logging.getLogger("Boot Admin")


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname).1s %(asctime).19s] %(message)s',
        datefmt='%y-%m-%d %H:%M:%S'
    )

    create_project()
