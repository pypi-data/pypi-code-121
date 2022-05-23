"""
Tiny puthon script for running the setup MeqQuert bash script
for first time users.
"""
import subprocess as sub
from pymedquery.config import config


def run_setup() -> None:
    sub.run(['sh', config.SHPATH])
