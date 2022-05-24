from pypers.steps.base.extract import ExtractBase


class Trademarks(ExtractBase):
    """
    Extract GETM archive
    """
    spec = {
        "version": "2.0",
        "descr": [
            "Returns the directory with the extraction"
        ]
    }

    def process(self):
        pass