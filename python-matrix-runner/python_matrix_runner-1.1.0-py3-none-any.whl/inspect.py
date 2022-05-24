# -*- coding: utf-8 -*-

import json
import sys

from argparse import ArgumentParser
from enum import Enum

from .config import Config
from .runner import Runner
from .axis import Axis


class InspectRunner(Runner):
    """Inspect a matrix runner script."""

    class JSONEncoder(json.JSONEncoder):
        """Custom JSONEncoder"""
        def default(self, o):
            if isinstance(o, Axis):
                return {'abbrev': o.abbrev, 'values': o.values, 'desc': o.desc}
            if isinstance(o, Config):
                return vars(o)
            if isinstance(o, Enum):
                return str(o)
            return super().default(o)

    def __init__(self, argv=None):
        super().__init__()

        parser = ArgumentParser()
        parser.add_argument("script", type=open, help="The Matrix Runner script to inspect.")
        args, argv = parser.parse_known_args(argv)

        exec(args.script.read(), globals())  # pylint: disable=exec-used

        self.add_axis(Axis.get_instances())
        success = self.run(argv)

        if success:
            dump = json.dumps({'axes': self._axes, 'matrix': self._matrix}, cls=self.JSONEncoder)
            print(dump)

        if not success:
            sys.exit(1)
        sys.exit(0)
