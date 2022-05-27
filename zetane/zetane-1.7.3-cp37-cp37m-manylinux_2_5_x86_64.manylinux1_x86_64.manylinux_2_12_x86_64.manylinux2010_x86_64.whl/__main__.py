import os
import subprocess
from pathlib import Path
from zetane.utils import get_binary
from zetane.context import Context

def run():
    zcontext = Context()
    zcontext.plain_launch()

if __name__ == '__main__':
    run()
