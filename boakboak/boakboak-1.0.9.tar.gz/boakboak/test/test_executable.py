# standard lib imports
import colorama as color

color.init()
import datetime as dt
from collections import defaultdict
import os, re, sys, time
import unittest

# test package imports
import boakboak.src.settings as sts
import boakboak.src.executable as executable


# print(f"\n__file__: {__file__}")


class TestExecutable(unittest.TestCase):
    @classmethod
    def setUpClass(cls, *args, **kwargs):
        cls.boakInstance = params.Params()
        cls.verbose = 0

    @classmethod
    def tearDownClass(cls, *args, **kwargs):
        try:
            pass
        except Exception as e:
            print(f"UnitTest, tearDownClass, e: {e}")


if __name__ == "__main__":
    unittest.main()
    print("done")
    exit()
