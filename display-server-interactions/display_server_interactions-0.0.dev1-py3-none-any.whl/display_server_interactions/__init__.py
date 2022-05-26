#!/usr/bin/python3
# -*- coding: utf-8 -*-

from platform import system as __system

__version__ = "0.0.dev1"

__os_name = __system().lower()

if __os_name == "linux":
    from .linux import DSI

elif __os_name == "windows":
    raise NotImplementedError("Windows is not yet implemented.")

elif __os_name == "darwin":
    raise NotImplementedError("MacOS is not yet implemented.")

else:
    raise NotImplementedError("Your OS is not supported.")

__all__ = ["DSI"]
