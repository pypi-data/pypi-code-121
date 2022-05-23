# -*- coding: utf-8 -*-

"""
csv writer
"""

from dfactory.core import Handler


class CsvWriter(Handler):
    """
    csv output
    """

    def __init__(self, **kwargs):
        self.filename = kwargs.get("path", "")
        self.file = None
        self.sep = kwargs.get('separator', ",")
        self.headers = kwargs.get('headers')
        self.format = None

    def is_created(self) -> bool:
        """check if writer ready to write"""
        return self.file is not None

    def __enter__(self):
        """prepare data"""
        self.file = open(self.filename, "w", encoding="utf-8")
        self.prepare_format_fun()
        if self.headers is not None:
            self.file.write(self.sep.join(self.headers) + "\n")

    def prepare_format_fun(self):
        """ prepare output format"""
        if self.headers is not None:
            self.format = lambda a: self.sep.join([str(a[k]) for k in self.headers])
        else:
            self.format = lambda a: self.sep.join([str(a[k]) for k in a])

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        close file if necessary
        """
        if self.file is not None:
            self.file.close()
        self.file = None

    @staticmethod
    def from_dict(cfg: dict):
        """
        create a CsvWriter from data
        :param cfg: cfg data
        :return: new CsvWriter object
        """
        return CsvWriter(**cfg)

    def load_data(self, cfg: dict):
        """
        load data
        :param cfg: config data
        :return: None
        """
        self.file = None
        self.filename = cfg.get("path")
        self.headers = cfg.get("headers")
        self.sep = cfg.get('separator', ",")

    def handle(self, item: dict):
        """
        save item to csv file
        :param item: item to handle
        :return: the same item
        """
        try:
            self.file.write(self.format(item))
            self.file.write("\n")
        except IOError:
            pass
        return item
