#!/usr/bin/env python3

import sys


class SomUtil:
    history_limit = 5

    def __init__(self):
        pass

    @staticmethod
    def print(msg_without_nl_cr):
        sys.stdout.write("{0}\n\r".format(msg_without_nl_cr))
        sys.stdout.flush()

    @staticmethod
    def rq(string):
        if string == "":
            return string
        return string.replace("'", "''")
