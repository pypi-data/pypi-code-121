#!/usr/bin/env python
# -*- coding: UTF-8 -*-


import logging


# TODO: consider incorporating these comments - https://blog.guilatrova.dev/how-to-log-in-python-like-a-pro/
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(filename)s : %(funcName)s() : %(lineno)d : %(message)s',
    level=logging.DEBUG)


class BaseObject(object):

    def __init__(self,
                 component_name: str):
        """
        Created:
            29-Sept-2021
            craig@grafflr.ai
        :param component_name:
            the component name
        """
        self.logger = logging.getLogger(component_name)
        isEnabledFor = self.logger.isEnabledFor
        self.isEnabledForDebug = isEnabledFor(logging.DEBUG)
        self.isEnabledForInfo = isEnabledFor(logging.INFO)
        self.isEnabledForWarning = isEnabledFor(logging.WARNING)

    def get_logger(self) -> logging.Logger:
        return self.logger

    def component_name(obj: object) -> str:
        return str(obj.__class__).split("<class '")[-1].split("'")[0]

    @staticmethod
    def uuid_generator() -> str:
        from uuid import uuid1
        return str(uuid1()).replace('-', '_')
