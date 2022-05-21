import glob
from typing import List

from pynextflow import Channel


class ChannelFromPath(Channel):
    pattern: str

    def __init__(self, pattern):
        super().__init__(f"Channel.fromPath(\"{pattern}\")")
        self.pattern = pattern

    def _generator(self):
        return glob.glob(self.pattern)


class ChannelFromList(Channel):
    values: List

    def __init__(self, values):
        body = ",".join(repr(v) for v in values)
        super().__init__(f"Channel.fromList([{body}])")
        self.values = values

    def _generator(self):
        return (v for v in self.values)
