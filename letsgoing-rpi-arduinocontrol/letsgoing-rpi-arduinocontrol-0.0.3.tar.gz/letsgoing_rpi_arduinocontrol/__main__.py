#!/usr/bin/env python3
import sys

from .Gui import GUI
from .Controller import controll



def main():
    gui = GUI()
    gui.run()
    controll.on_exit()
    sys.exit(0)

if __name__ == "__main__":
    main()