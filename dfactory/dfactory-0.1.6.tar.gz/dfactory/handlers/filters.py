"""
filters are class that filter some items base on some rules
"""

from dfactory.core import Handler
from dfactory.handlers.matches import Match


class Filter(Handler):
    """
    Filter filter some type of item base with a matcher,
    the one that match are skipped
    """

    def __init__(self):
        super().__init__()
        self.matcher = None

    def load_data(self, cfg: dict):
        self.matcher = Match.from_dict(cfg["matcher"])

    def handle(self, item: dict) -> dict:
        if self.matcher.match(item):
            return None
        return item
