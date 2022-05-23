# coding=utf-8
from __future__ import absolute_import, print_function

import contextlib
import copy
import itertools
from collections import defaultdict

from suanpan import error, runtime
from suanpan.arguments.auto import AutoArg
from suanpan.interfaces import (
    HasArguments,
    HasCallHooks,
    HasCleanHooks,
    HasExitHooks,
    HasInitHooks,
    HasSaveHooks,
)
from suanpan.log import logger
from suanpan.objects import Context


class Arguments(Context):
    @classmethod
    def froms(cls, *args):
        context = cls()
        context.update({arg.key: arg.value for arg in args if arg.key})
        context.update({arg.alias: arg.value for arg in args if arg.alias})
        return context


class Result(Context):
    pass


class Component(
    HasArguments, HasInitHooks, HasCallHooks, HasSaveHooks, HasCleanHooks, HasExitHooks
):
    def __init__(self):
        super().__init__()
        self.runFunc = None
        self.arguments = defaultdict(list)
        self.argsDict = {}

    def __call__(self, *arg, **kwargs):
        return self.run(*arg, **kwargs)

    def start(self, *arg, **kwargs):
        return self.run(*arg, **kwargs)

    @property
    def name(self):
        return self.runFunc.__name__

    @runtime.processrun
    def run(self, *arg, **kwargs):
        self.callBeforeInitHooks()
        context = self.init(*arg, **kwargs)
        self.callAfterInitHooks(context)
        self.registerBeforeExitHooks(context)

        self.callBeforeCallHooks(context)
        if not self.runFunc:
            raise error.ComponentHandlerNotSet()
        if not callable(self.runFunc):
            raise error.ComponentHandlerNotCallable(self.name)
        results = self.runFunc(context)
        self.callAfterCallHooks(context)

        self.callBeforeSaveHooks(context)
        outputs = self.save(results)
        self.callAfterSaveHooks(context)

        self.callBeforeCleanHooks(context)
        self.clean()
        self.callAfterCleanHooks()

        return outputs

    def init(self, *args, **kwargs):
        self.argsDict = self.getArgsDict(*args, **kwargs)
        globalArgs = self.loadGlobalArguments(self.argsDict)
        self.initBase(globalArgs)
        context = self._getContext(globalArgs)
        args = self.loadComponentArguments(self.argsDict)
        context.update(args=args)
        return context

    def load(self, args, argsDict=None):
        logger.debug("Loading Arguments:")
        argsDict = argsDict or self.argsDict
        for arg in args:
            if isinstance(arg, AutoArg):
                arg.setBackend(argtype="inputs")
        args = self.loadFormatArguments(args, argsDict)
        return Arguments.froms(*args)

    def loadGlobalArguments(self, argsDict=None):
        logger.debug("Loading Global Arguments:")
        argsDict = argsDict or self.argsDict
        args = self.getGlobalArguments()
        args = self.loadFormatArguments(args, argsDict)
        return Arguments.froms(*args)

    def loadComponentArguments(self, argsDict=None):
        logger.debug("Loading Component Arguments:")
        argsDict = argsDict or self.argsDict
        args = copy.deepcopy(self.getArguments(exclude="outputs"))
        args = self.loadFormatArguments(args, argsDict)
        return Arguments.froms(*args)

    def initBase(self, args):
        pass

    @contextlib.contextmanager
    def context(self, args=None):  # pylint: disable=unused-argument
        yield Context()

    def _getContext(self, *args, **kwargs):
        self.contextManager = self.context(  # pylint: disable=attribute-defined-outside-init
            *args, **kwargs
        )
        return next(self.contextManager.gen)  # pylint: disable-msg=e1101

    def _closeContext(self):
        try:
            next(self.contextManager.gen)  # pylint: disable-msg=e1101
        except StopIteration:
            pass

    def getArguments(self, include=None, exclude=None):
        includes = set(self.arguments.keys() if not include else self._list(include))
        excludes = set([] if not exclude else self._list(exclude))
        includes = includes - excludes
        argumentsLists = [self.arguments[c] for c in includes]
        return list(itertools.chain(*argumentsLists))

    def save(self, results, args=None, **_):
        logger.debug("Saving...")
        if args:
            for arg in args:
                if isinstance(arg, AutoArg):
                    arg.setBackend(argtype="outputs")
        else:
            args = copy.deepcopy(self.getArguments(include="outputs"))
        args = self.loadCleanArguments(args, self.argsDict)
        return self.saveOutputs(args, results)

    def saveOutputs(self, args, results):
        if len(args) > 1:
            return self.saveMutipleOutputs(args, results)
        if len(args) == 1:
            return self.saveOneOutput(args[0], results)
        return None

    def saveMutipleOutputs(self, args, results):
        if isinstance(results, (tuple, list)):
            results = (Result.froms(value=result) for result in results)
            return self.saveArguments(args, results)
        if isinstance(results, dict):
            tmp = [
                (
                    argument,
                    Result.froms(
                        value=self.getArgumentValueFromDict(results, argument)
                    ),
                )
                for argument in args
                if self.getArgumentValueFromDict(results, argument) is not None
            ]
            if not tmp:
                return self.saveOneOutput(args[0], results)
            args, results = zip(*tmp)
            return self.saveArguments(args, results)
        raise error.ComponentError(f"Incorrect results {results}")

    def saveOneOutput(self, arg, results):
        result = (
            Result.froms(value=self.getArgumentValueFromDict(results, arg))
            if isinstance(results, dict) and self.hasArgumentValueFromDict(results, arg)
            else Result.froms(value=results)
        )
        return {arg.key: arg.save(result)}

    def clean(self):
        self._closeContext()

    def addArgument(self, arg, argtype="args", reverse=False):
        if reverse:
            self.arguments[argtype].insert(0, arg)
        else:
            self.arguments[argtype].append(arg)

    def use(self, func):
        self.runFunc = func
        return self

    def arg(self, argument, argtype="args", reverse=False):
        if isinstance(argument, AutoArg):
            argument.setBackend(argtype=argtype)
        self.addArgument(argument, argtype=argtype, reverse=reverse)
        return lambda *args, **kwargs: self

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

    def _list(self, params=None):
        return [params] if isinstance(params, str) else list(params)
