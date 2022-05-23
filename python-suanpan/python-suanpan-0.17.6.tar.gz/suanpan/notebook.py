# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.components import Component
from suanpan.log import logger


class Notebook(object):
    def __init__(self, component=Component, name="Notebook", runFunc=None):
        def defaultRunFunc(*args, **kwargs):  # pylint: disable=unused-argument
            pass

        self.name = name
        self.componentClass = component
        self.runFunc = runFunc or defaultRunFunc
        self.runFunc.__name__ = self.name
        self.component = self.componentClass(self.runFunc)

    def init(self):
        self.beforeInit()
        context = self.component.init()
        self.afterInit(context)
        return context

    def beforeInit(self):
        logger.logDebugInfo()
        logger.debug(f"Notebook {self.name} starting...")

    def afterInit(self, context):
        pass

    def save(self, context, results):
        self.beforeSave(context)
        results = self.component.save(context, results)
        self.afterSave(context)

    def beforeSave(self, context):
        pass

    def afterSave(self, context):  # pylint: disable=unused-argument
        logger.debug(f"Notebook {self.name} done.")

    def arg(self, *args, **kwargs):
        kwargs.update(reverse=False)
        decorator = self.componentClass.arg(*args, **kwargs)
        self.component = decorator(self.component)
        return self.component

    def input(self, *args, **kwargs):
        kwargs.update(argtype="inputs")
        return self.arg(*args, **kwargs)

    def output(self, *args, **kwargs):
        kwargs.update(argtype="outputs")
        return self.arg(*args, **kwargs)

    def param(self, *args, **kwargs):
        kwargs.update(argtype="params")
        return self.arg(*args, **kwargs)

    def column(self, *args, **kwargs):
        kwargs.update(argtype="columns")
        return self.arg(*args, **kwargs)
