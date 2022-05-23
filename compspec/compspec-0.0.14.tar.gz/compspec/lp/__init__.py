__author__ = "Vanessa Sochat"
__copyright__ = "Copyright 2022, Vanessa Sochat"
__license__ = "MPL 2.0"

from compspec.logger import logger
import os

here = os.path.dirname(os.path.abspath(__file__))


def get_facts(names):
    """
    Retrieve logic programs by name, if they exists.
    We do not continue if they do not!
    """
    if not isinstance(names, list):
        names = [names]

    logic_programs = []

    for name in names:
        # First attempt - a full path was provided
        if os.path.exists(name):
            logic_programs.append(name)
            continue

        # Second attempt - logic program provided here
        path = os.path.join(here, name)
        if not os.path.exists(path):
            logger.exit(f"{path} does not exist.")
        logic_programs.append(path)

    return logic_programs
