# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan import asyncio  # noqa
from suanpan.g import g  # noqa
from suanpan.run import cli, helper, env, run  # noqa

__version__ = "0.17.6"

if __name__ == "__main__":
    print(f"Suanpan SDK (ver: {__version__})")
