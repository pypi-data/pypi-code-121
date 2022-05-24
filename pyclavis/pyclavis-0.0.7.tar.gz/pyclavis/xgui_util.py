import sys
import subprocess
import time

import pyautogui

import pyperclip

from .logging import log, print_t, print_e


def write_clipboard(t):
    pyperclip.copy(t)


def read_clipboard():
    return pyperclip.paste()


def clear_clipboard():
    write_clipboard("")


# pyautogui additional sequences to be pressed
# do not use
# subject to change
def handle_hotkey(c):
    esc = [
        ("shift", ["/", "&", "?", "*"]),
        ("altright", ["@", "[", "]", "{", "}", "\\", "~"]),
    ]
    for hotk, chrs in esc:
        if c in chrs:
            return (hotk, c)


#
# using clipboard due to a bug in pyautogui and x11 on different platforms
#
# e.g.
#
# https://github.com/asweigart/pyautogui/issues/186
# https://github.com/asweigart/pyautogui/issues/93
#

_send_keys_meth = False

#
# todo
# rework, as soon as bugs are resolved
#


_esc_keys = {
    "\n": "enter",
    "\t": "tab",
}


def _no_esc_key(s):
    for c in s:
        if c in _esc_keys:
            return False
    return True


DELAY_KEY = 250
CHUNK_SIZE = 5


def send_keys(t, interval=DELAY_KEY / 1000, chunk=CHUNK_SIZE, to_term=False):
    if _send_keys_meth:
        pyautogui.write(t, interval=interval)
    else:
        for c in [t[index : index + chunk] for index in range(0, len(t), chunk)]:
            if _no_esc_key(c):
                write_clipboard(c)
            else:
                for ch in c:
                    print_t("sleep", interval)
                    time.sleep(interval)
                    if ch in _esc_keys:
                        pyautogui.press(_esc_keys[ch])
                        continue
                    write_clipboard(ch)
                    send_paste(to_term)
            if interval > 0:
                print_t("sleep", interval)
                time.sleep(interval)
            send_paste(to_term)
        clear_clipboard()


def send_paste(to_term):
    if to_term:
        # linux terminal paste
        pyautogui.hotkey("ctrl", "shift", "v")
    else:
        pyautogui.hotkey("ctrl", "v")


def send_combined(hotk, ch):
    pyautogui.hotkey(hotk, ch)


#


def open_file_explorer(d):
    if sys.platform == "win32":
        subprocess.Popen(["start", d], shell=True)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", d])
    else:
        subprocess.Popen(["xdg-open", d])
