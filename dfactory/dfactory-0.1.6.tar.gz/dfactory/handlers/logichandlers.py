"""
logic handlers
"""
from dfactory.core import Handler


class LinkHandler(Handler):
    """
    LinkHandler
    a group of handler
    run in sequence until one success
    """

    def __init__(self):
        super().__init__()
        self.handlers = []
        self.matches = {}

    def check(self, item: dict):
        """
        check if item match the rules
        :param item: item to check
        :return: True if match else False
        """
        for k, values in self.matches.items():
            keys = k.split(".")
            obj = item
            for key in keys:
                obj = obj.get(key)
                if obj is None:
                    return False
            if obj != values:
                return False
        return True

    def handle(self, item: dict) -> dict:
        """
        handle with a group of handler and return the first success result
        :param item: item to handle
        :return: new object if one the handlers success otherwise the origin item
        """
        for handler in self.handlers:
            obj = handler.handle(item)
            if self.check(obj):
                return obj
        return item

    def load_data(self, cfg: dict):
        self.matches = cfg["match"]
        for item in cfg["handlers"]:
            handler = self.from_dict(item)
            if handler is not None:
                self.handlers.append(handler)
