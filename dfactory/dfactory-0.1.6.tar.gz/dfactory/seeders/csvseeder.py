# -*- coding: utf-8 -*-

"""
csv seeder
"""
from dfactory.core import Seeder


class CsvSeeder(Seeder):
    """
    a seeder that generate dict item from csv file line by line
    """

    def __init__(self, **kwargs):
        self.src_fn = kwargs.get("path")
        self._reader = None
        self.sep = kwargs.get("separator", ",")
        self.keys = kwargs.get("keys", [])

    def iter(self):
        with self:
            for line in self._reader:
                item = self.line2item(line.strip())
                if item is None:
                    continue
                yield item

    def load_data(self, cfg: dict):
        self.close()
        self.src_fn = cfg["path"]
        self.sep = cfg.get("separator", self.sep)
        self.keys = cfg["keys"]

    def line2item(self, line: str):
        """
        convert text line to item
        :param line: line from source file
        :return: None if no more item else a item of type dict
        """
        parts = line.split(self.sep, maxsplit=len(self.keys))
        if len(parts) != len(self.keys):
            return None
        return {self.keys[k]: parts[k] for k in range(len(self.keys))}

    def close(self):
        """
        close file
        :return:  None
        """
        if self._reader is not None:
            self._reader.close()
        self._reader = None

    def __enter__(self):
        if self._reader is None:
            self._reader = open(self.src_fn, encoding="utf-8")

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    @staticmethod
    def from_dict(cfg: dict):
        """create a CsvSeeder from configure"""
        return CsvSeeder(**cfg)
