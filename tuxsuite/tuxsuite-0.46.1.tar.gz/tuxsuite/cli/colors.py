# -*- coding: utf-8 -*-

cyan = "\033[36m"
green = "\033[32m"
red = "\033[91m"
white = "\033[37m"
yellow = "\033[33m"
reset = "\033[0m"


def state(s, r):
    if s == "waiting":
        return white
    if s == "provisioning":
        return white
    if s == "running":
        return cyan
    if s == "finished":
        if r == "pass":
            return green
        if r == "fail":
            return red
        if r == "error":
            return red
    raise NotImplementedError()
