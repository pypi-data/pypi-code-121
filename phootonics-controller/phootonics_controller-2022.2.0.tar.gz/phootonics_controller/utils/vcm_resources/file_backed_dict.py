# -*- coding: utf-8 -*-
"""
Created by gregory on 18.03.16

Copyright 2016 Alpes Lasers SA, Neuchatel, Switzerland
"""
import json
import logging

logger = logging.getLogger(__name__)

__author__ = 'gregory'
__copyright__ = "Copyright 2016, Alpes Lasers SA"


class FileBackedDict(dict):
    """Dictionary that automatically saves the changes to a file"""

    def __init__(self, filepath):
        super(FileBackedDict, self).__init__()
        self.filepath = filepath
        if self.filepath is not None:
            try:
                self.load()
            except IOError:
                pass  # not an error if the file does not exist at creation time.

    def load(self, filepath=None, clear=False):
        if filepath is not None:
            self.filepath = filepath
        try:
            with open(self.filepath) as fp:
                dct = json.load(fp)
        except IOError:
            dct = {}
        if clear:
            self.clear()
        self.update(dct)

    def save(self, filepath=None):
        if filepath is not None:
            self.filepath = filepath
        if self.filepath is not None:
            with open(self.filepath, 'w') as fp:
                json.dump(self, fp)

    def update(self, E=None, **F):
        super(FileBackedDict, self).update(E, **F)
        self.save()

    def setdefault(self, k, d=None):
        super(FileBackedDict, self).setdefault(k, d)
        self.save()

    def __setitem__(self, key, value):
        super(FileBackedDict, self).__setitem__(key, value)
        self.save()

    def __delitem__(self, key):
        super(FileBackedDict, self).__delitem__(key)
        self.save()

    def clear(self):
        super(FileBackedDict, self).clear()
        self.save()
