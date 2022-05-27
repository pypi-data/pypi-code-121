import os
from tuxmake.logging import warning


def getenv(variable, replacement):
    value = os.getenv(variable)
    if value:
        warning(
            f"The environment {variable} is deprecated; please use {replacement} instead"
        )
    return value
