#!/usr/bin/python3
# -*- coding: utf-8 -*-

from . import DSI


def main() -> None:
    window = DSI.get_active_window()

    print("Active window: ")
    print("\tName: {}".format(window.name))
    print("\tPID: {}".format(window.pid))
    if window.xid:
        print("\tXID: {}".format(window.xid))
    print("\tGeometry: {}".format(window.geometry))


if __name__ == "__main__":
    main()
