#!/usr/bin/env python3
# -*- coding: utf-8 -*-

###################
#    This package implements tools to build python package and tools.
#    Copyright (C) 2022  Maurice Lambert

#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.

#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.

#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <https://www.gnu.org/licenses/>.
###################

"""
This package implements tools to build python package and tools.

>>> from WindowsTerminal import *
>>> print("\\x1b[32mabc\\x1b[0m")
←[32mabc←[0m
>>> active_virtual_terminal()
True
>>> print("\\x1b[32mabc\\x1b[0m")
abc
>>> desactive_virtual_terminal()
True
>>> print("\\x1b[32mabc\\x1b[0m")
←[32mabc←[0m
>>> desactive_virtual_terminal()
False
>>> active_virtual_terminal()
True
>>> active_virtual_terminal()
False
>>> persistent_virtual_terminal()
>>> delete_persistent_virtual_terminal()
>>> persistent_terminal_transparency(0x4d)
>>> delete_persistent_terminal_transparency()
>>> set_terminal_transparency(0)
True
>>> set_terminal_transparency(255)
True
>>> set_color_transparency(0x00000000)
True
>>> set_color_transparency(0x000000FF)
True
>>>
"""

__version__ = "0.0.1"
__author__ = "Maurice Lambert"
__author_email__ = "mauricelambert434@gmail.com"
__maintainer__ = "Maurice Lambert"
__maintainer_email__ = "mauricelambert434@gmail.com"
__description__ = """
This package implements tools to build python package and tools.
"""
license = "GPL-3.0 License"
__url__ = "https://github.com/mauricelambert/PythonToolsKit"

copyright = """
PythonToolsKit  Copyright (C) 2022  Maurice Lambert
This program comes with ABSOLUTELY NO WARRANTY.
This is free software, and you are welcome to redistribute it
under certain conditions.
"""
__license__ = license
__copyright__ = copyright

__all__ = [
    "desactive_virtual_terminal",
    "active_virtual_terminal",
    "persistent_virtual_terminal",
    "delete_persistent_virtual_terminal",
    "persistent_terminal_transparency",
    "delete_persistent_terminal_transparency",
    "set_terminal_transparency",
    "set_color_transparency",
]

from os import name

set_terminal_transparency = (
    set_color_transparency
) = active_virtual_terminal = desactive_virtual_terminal = lambda: False
delete_persistent_terminal_transparency = (
    persistent_terminal_transparency
) = (
    persistent_virtual_terminal
) = delete_persistent_virtual_terminal = lambda: None

if name == "nt":

    from winreg import (
        CreateKey,
        OpenKey,
        SetValueEx,
        CloseKey,
        HKEY_CURRENT_USER,
        KEY_WRITE,
        REG_DWORD,
        DeleteValue,
    )
    from ctypes.wintypes import COLORREF, DWORD, BYTE
    from ctypes import windll, byref, WinDLL

    global default_in_mode, default_out_mode, is_active

    default_in_mode: DWORD = DWORD()
    default_out_mode: DWORD = DWORD()

    is_active: bool = False

    OUT_ENABLE_VIRTUAL_TERMINAL_PROCESSING: int = 0x0004
    IN_ENABLE_VIRTUAL_TERMINAL_INPUT: int = 0x0200
    OUT_DISABLE_NEWLINE_AUTO_RETURN: int = 0x0008

    kernel32: WinDLL = windll.kernel32
    user32: WinDLL = windll.user32

    _FuncPtr: type = kernel32._FuncPtr

    GetStdHandle: _FuncPtr = kernel32.GetStdHandle
    GetConsoleMode: _FuncPtr = kernel32.GetConsoleMode
    SetConsoleMode: _FuncPtr = kernel32.SetConsoleMode

    STDIN: int = GetStdHandle(-10)
    STDOUT: int = GetStdHandle(-11)
    STDERR: int = GetStdHandle(-12)

    LWA_ALPHA: DWORD = DWORD(0x00000002)
    LWA_COLORKEY: DWORD = DWORD(0x00000001)

    def desactive_virtual_terminal() -> bool:

        """
        This function desactive terminal colors on Windows.

        >>> print("\\x1b[32mabc\\x1b[0m")
        ←[32mabc←[0m
        >>> active_virtual_terminal()
        True
        >>> print("\\x1b[32mabc\\x1b[0m")
        abc
        >>> desactive_virtual_terminal()
        True
        >>> print("\\x1b[32mabc\\x1b[0m")
        ←[32mabc←[0m
        >>> desactive_virtual_terminal()
        False
        >>>
        """

        global default_in_mode, default_out_mode, is_active

        if not is_active:
            return False

        if not SetConsoleMode(STDOUT, default_out_mode):
            return False

        # if not SetConsoleMode(STDIN, default_in_mode):
        #    return False

        is_active = False
        return True

    def active_virtual_terminal() -> bool:

        """
        This function active terminal colors on Windows.

        return True on success and False on fail.

        doc: https://docs.microsoft.com/fr-fr/windows/console/console-virtual-terminal-sequences#code-try-1

        >>> print("\\x1b[32mabc\\x1b[0m")
        ←[32mabc←[0m
        >>> active_virtual_terminal()
        True
        >>> print("\\x1b[32mabc\\x1b[0m")
        abc
        >>> active_virtual_terminal()
        False
        >>>
        """

        global default_in_mode, default_out_mode, is_active

        if is_active:
            return False

        if not GetConsoleMode(STDOUT, byref(default_out_mode)):
            return False

        if not GetConsoleMode(STDIN, byref(default_in_mode)):
            return False

        new_out_mode = (
            OUT_ENABLE_VIRTUAL_TERMINAL_PROCESSING
            | OUT_DISABLE_NEWLINE_AUTO_RETURN
        )
        new_in_mode = IN_ENABLE_VIRTUAL_TERMINAL_INPUT

        new_out_mode = DWORD(default_out_mode.value | new_out_mode)
        new_in_mode = DWORD(default_in_mode.value | new_in_mode)

        if not SetConsoleMode(STDOUT, new_out_mode):
            return False

        # if not SetConsoleMode(STDIN, new_in_mode):
        #    return False

        is_active = True
        return True

    def persistent_virtual_terminal() -> None:

        """
        This function adds a virtual terminal persistent
        configuration using the registry.

        >>> persistent_virtual_terminal()
        >>>
        """

        path = "Console"
        CreateKey(HKEY_CURRENT_USER, path)
        key = OpenKey(HKEY_CURRENT_USER, path, 0, KEY_WRITE)
        SetValueEx(key, "VirtualTerminalLevel", 0, REG_DWORD, 1)
        CloseKey(key)

    def delete_persistent_virtual_terminal() -> None:

        """
        This function deletes the virtual terminal persistent
        configuration using the registry.

        >>> delete_persistent_virtual_terminal()
        >>>
        """

        path = "Console"
        CreateKey(HKEY_CURRENT_USER, path)
        key = OpenKey(HKEY_CURRENT_USER, path, 0, KEY_WRITE)
        DeleteValue(key, "VirtualTerminalLevel")
        CloseKey(key)

    def persistent_terminal_transparency(level: int) -> None:

        """
        This function adds a terminal transparency persistent
        configuration using the registry.

        'level' argument should be an integer between 77-255
        (77 (0x4D) is the most transparent level and 255
        (0xFF) is the most opaque level)

        >>> persistent_terminal_transparency(0x4d)
        >>>
        """

        path = "Console"
        CreateKey(HKEY_CURRENT_USER, path)
        key = OpenKey(HKEY_CURRENT_USER, path, 0, KEY_WRITE)
        SetValueEx(key, "WindowAlpha", 0, REG_DWORD, 1)
        CloseKey(key)

    def delete_persistent_terminal_transparency() -> None:

        """
        This function deletes the terminal transparency
        persistent configuration using the registry.

        >>> delete_persistent_terminal_transparency()
        >>>
        """

        path = "Console"
        CreateKey(HKEY_CURRENT_USER, path)
        key = OpenKey(HKEY_CURRENT_USER, path, 0, KEY_WRITE)
        DeleteValue(key, "WindowAlpha")
        CloseKey(key)

    def set_terminal_transparency(level: int) -> bool:

        """
        This function sets the terminal transparency on Windows.

        'level' argument should be an integer between 0-255
        (0 is the most transparent level and
        255 is the most opaque level)

        >>> set_terminal_transparency(0)
        True
        >>> set_terminal_transparency(255)
        True
        >>>
        """

        active_windows = (
            user32.GetActiveWindow() or user32.GetForegroundWindow()
        )

        if user32.SetLayeredWindowAttributes(
            active_windows, 0, BYTE(level), LWA_ALPHA
        ):
            return True

        return False

    def set_color_transparency(color: int) -> bool:

        """
        This function sets the transparent color of the window.

        'level' argument should be an integer between 0-4294967295
        (0 (0x00000000) is black, 16777215 (0x00FFFFFF) is white,
        255 (0x000000FF) is blue, 65280 (0x0000FF00) is green and
        16711680 (0x00FF0000) is red)

        >>> set_color_transparency(0x00000000)
        True
        >>> set_color_transparency(0x000000FF)
        True
        >>>
        """

        active_windows = (
            user32.GetActiveWindow() or user32.GetForegroundWindow()
        )

        if user32.SetLayeredWindowAttributes(
            active_windows, COLORREF(color), 0, LWA_COLORKEY
        ):
            return True

        return False

    if __name__ == "__main__":
        import doctest

        doctest.testmod(verbose=True)
