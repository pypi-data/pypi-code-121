# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app.base import BaseApp
from suanpan.docker import DockerComponent as Handler


class DockerApp(BaseApp):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.handler = Handler()

    def __call__(self, funcOrApp):
        if not isinstance(funcOrApp, BaseApp):
            self.handler.use(funcOrApp)
        return self

    @property
    def name(self):
        return self.handler.name

    def start(self, *args, **kwargs):
        super().start(*args, **kwargs)
        return self.handler.start(*args, **kwargs)

    def input(self, argument):
        self.handler.input(argument)
        return self

    def output(self, argument):
        self.handler.output(argument)
        return self

    def param(self, argument):
        self.handler.param(argument)
        return self

    def column(self, argument):
        self.handler.column(argument)
        return self

    def beforeInit(self, hook):
        self.handler.addBeforeInitHooks(hook)
        return hook

    def afterInit(self, hook):
        self.handler.addAfterInitHooks(hook)
        return hook

    def beforeCall(self, hook):
        self.handler.addBeforeCallHooks(hook)
        return hook

    def afterCall(self, hook):
        self.handler.addAfterCallHooks(hook)
        return hook

    def beforeExit(self, hook):
        self.handler.addBeforeExitHooks(hook)
        return hook

    def load(self, *args, **kwargs):
        return self.handler.load(*args, **kwargs)

    def save(self, *args, **kwargs):
        return self.handler.save(*args, **kwargs)

    def send(self, *args, **kwargs):
        return self.handler.save(*args, **kwargs)
