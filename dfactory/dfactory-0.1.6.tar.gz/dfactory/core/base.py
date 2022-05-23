# -*- coding: utf-8 -*-

"""
base classes

Handler is a class describe a set of actions on data item

Seeder is the data generator to generate data to feed the pipeline
"""

import abc
from abc import ABC

from .utils import import_class


class LoaderMixin:
    """
    a class like a interface to enable to load from config
    """

    @staticmethod
    def from_dict(cfg: dict):
        """
       create a new object from config
       :param cfg: data to create new HandlerBase
       :return: new object if success otherwise None
       """
        cfg_class = import_class(cfg["class"])
        obj = cfg_class()
        obj.load_data(cfg)
        return obj

    def load_data(self, cfg: dict):
        """
        load data from dict
        :param cfg: config data
        :return:
        """


class HandlerBase(LoaderMixin):
    """
    handler base
    """

    @abc.abstractmethod
    def handle(self, item: dict) -> dict:
        """
        abstract handle function
        :param item: item to be handled
        :return: item
        """
        raise NotImplementedError("virtual function called")


class Handler(HandlerBase, ABC):
    """
    common handler with some actions before or after pipeline starts
    """

    def __enter__(self):
        self.on_create()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.on_destroy()

    def on_create(self):
        """
        action before ready to run pipeline handle
        :return: None
        """

    def on_destroy(self):
        """
        actions after pipeline handle is done
        :return: None
        """


class Seeder(LoaderMixin):
    """
    seeder to feed pipeline
    """

    def iter(self) -> dict:
        """
        generate item
        :return: a object in dict type if there is still items to generate otherwise None
        """
        raise NotImplementedError('virtual function called')


class CondHandler(Handler):
    """
    condition handler to handle part of the items passed in
    """

    @abc.abstractmethod
    def check(self, item: dict) -> bool:
        """
        check if item shall be handled
        :param item: item to check
        :return: True if the item shell be handle otherwise False
        """
        raise NotImplementedError('virtual function called')

    @abc.abstractmethod
    def operate(self, item: dict) -> dict:
        """
        actions
        :param item: item to be handle
        :return:
        """
        raise NotImplementedError('virtual function called')

    def handle(self, item: dict) -> dict:
        """
        main handle function
        :param item: item
        :return: item
        """
        if self.check(item):
            return self.operate(item)
        return item
