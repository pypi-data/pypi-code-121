# -*- coding: utf-8 -*-

from argparse import Namespace


class Config(Namespace):
    """Config wrapper"""

    class Any:
        """Any object"""
        def match(self, _):
            """Match"""
            return not self

    def __getattr__(self, item):
        return self.Any()
