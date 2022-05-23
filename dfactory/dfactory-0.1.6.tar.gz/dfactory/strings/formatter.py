"""
String formatter Handler
"""

from dfactory.core import Handler


class StringFormatter(Handler):
    """
    form a string field with specified keys
    """

    def __init__(self):
        super().__init__()
        self.keys = []
        self.dst = None
        self.format = ""

    def handle(self, item: dict) -> dict:
        item[self.dst] = self.format.format_map({k: item.get(k, "") for k in self.keys})
        return item

    def load_data(self, cfg: dict):
        self.keys = cfg["keys"]
        self.dst = cfg["dst"]
        self.format = cfg["format"]
