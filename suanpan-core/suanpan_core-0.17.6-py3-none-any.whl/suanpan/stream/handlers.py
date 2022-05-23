# coding=utf-8
from __future__ import absolute_import, print_function

import contextlib
import copy

from suanpan import error, g
from suanpan.arguments.auto import AutoArg
from suanpan.components import Arguments, Component
from suanpan.log import logger
from suanpan.stream.objects import Context


class Handler(Component):
    def run(self, stream, message, *arg, **kwargs):
        self.callBeforeInitHooks()
        context = self.init(stream, message)
        self.callAfterInitHooks(context)

        self.callBeforeCallHooks(context)
        if not self.runFunc:
            raise error.ComponentHandlerNotSet()
        if not callable(self.runFunc):
            raise error.ComponentHandlerNotCallable(self.name)
        results = self.runFunc(stream, context, *arg, **kwargs)
        self.callAfterCallHooks(context)

        self.callBeforeSaveHooks(context)
        outputs = self.save(results, message=message)
        self.callAfterSaveHooks(context)

        self.callBeforeCleanHooks(context)
        self.clean()
        self.callAfterCleanHooks()

        return outputs

    def beforeInit(self):
        logger.debug(f"Handler {self.name} starting...")

    def init(self, stream, message):  # pylint: disable=unused-argument
        self.argsDict = self.getArgsDict(message)
        context = self._getContext(message)
        args = self.loadComponentArguments(self.argsDict)
        context.update(args=args)
        return context

    @contextlib.contextmanager
    def context(self, message):
        yield Context.froms(message=message)

    def getArgsDict(self, message):
        return message or {}

    def load(self, args, argsDict=None):
        argsDict = argsDict or self.argsDict
        logger.debug("Loading Arguments:")
        for key, value in argsDict.items():
            logger.debug(f"{key}: {value}")
        return Context.froms(argsDict)

    def loadComponentArguments(self, argsDict=None):
        argsDict = argsDict or self.argsDict
        logger.debug("Loading Component Arguments:")
        logger.debug(f"Inputs: {argsDict}")
        return Context.froms(argsDict)

    def save(self, results, args=None, message=None):  # pylint: disable=unused-argument
        logger.debug("Saving...")
        logger.debug(f"Outputs: {results}")
        return results

    def afterSave(self, context):  # pylint: disable=unused-argument
        logger.debug(f"Handler {self.name} done.")


class CallHandler(Handler):
    def __init__(self):
        super().__init__()
        self._input_arguments = []

    def init(self, stream, message):
        context = super().init(stream, message)
        context.args.update(stream.args)
        return context

    def load(self, args, argsDict=None):
        logger.debug("Loading Arguments:")
        argsDict = argsDict or self.argsDict
        argsDict = {
            f"{arg.key}": argsDict.get(f"in{i + 1}")
            for i, arg in enumerate(args)
            if argsDict.get(f"in{i + 1}") is not None
        }
        for arg in args:
            if isinstance(arg, AutoArg):
                arg.setBackend(argtype="inputs")
        args = self.loadFormatArguments(args, argsDict)
        return Arguments.froms(*args)

    def loadFormatArguments(self, arguments, argsDict):
        arguments = super().loadFormatArguments(arguments, argsDict)
        self._input_arguments = arguments
        # for argument in arguments:
        #     argument.clean()
        return arguments

    def loadComponentArguments(self, argsDict=None):
        logger.debug("Loading Component Arguments:")
        argsDict = argsDict or self.argsDict
        arguments = copy.deepcopy(self.getArguments(exclude="outputs"))
        argsDict = {
            f"{arg.key}": argsDict.get(f"in{i + 1}")
            for i, arg in enumerate(arguments)
            if argsDict.get(f"in{i + 1}") is not None
        }
        argsDict = argsDict or self.argsDict
        args = self.loadFormatArguments(arguments, argsDict)
        return Arguments.froms(*args)

    def save(self, results, args=None, message=None):
        logger.debug("Saving...")
        if args:
            for arg in args:
                if isinstance(arg, AutoArg):
                    arg.setBackend(argtype="outputs")
        else:
            args = copy.deepcopy(self.getArguments(include="outputs"))
        shortRequestID = self.shortenRequestID(message["id"])
        outputArgsDict = {
            arg.key: arg.getOutputTmpValue(
                "studio",
                g.userId,
                "tmp",
                g.appId,
                shortRequestID,
                g.nodeId,
                f"out{i + 1}",
            )
            for i, arg in enumerate(args)
        }
        args = self.loadCleanArguments(args, outputArgsDict)
        return self.saveOutputs(args, results)

    def saveOutputs(self, args, results):
        if results is not None:
            outputs = super().saveOutputs(args, results)
            outputs = self.formatAsOuts(args, outputs)
            outputs = self.stringifyOuts(outputs)
            return outputs
        return None

    def saveOneOutput(self, arg, results):
        result = super().saveOneOutput(arg, results)
        arg.clean()
        return result

    def saveArguments(self, arguments, results):
        result = super().saveArguments(arguments, results)
        for argument in arguments:
            argument.clean()
        return result

    def formatAsOuts(self, args, results):
        return {
            f"out{i + 1}": self.getArgumentValueFromDict(results, arg)
            for i, arg in enumerate(args)
        }

    def stringifyOuts(self, outs):
        return {k: str(v) for k, v in outs.items() if v is not None}

    def shortenRequestID(self, requestID):
        return requestID.replace("-", "")

    def clean(self):
        super(CallHandler, self).clean()
        for argument in self._input_arguments:
            argument.clean()


class TriggerHandler(CallHandler):
    pass


class SIOHandler(Handler):
    def run(self, stream, message, sid, *arg, **kwargs):
        self.callBeforeInitHooks()
        context = self.init(stream, message, sid)
        self.callAfterInitHooks(context)

        self.callBeforeCallHooks(context)
        if not self.runFunc:
            raise error.ComponentHandlerNotSet()
        if not callable(self.runFunc):
            raise error.ComponentHandlerNotCallable(self.name)
        results = self.runFunc(stream, context, *arg, **kwargs)
        self.callAfterCallHooks(context)

        self.callBeforeSaveHooks(context)
        outputs = self.save(results, message=message)
        self.callAfterSaveHooks(context)

        self.callBeforeCleanHooks(context)
        self.clean()
        self.callAfterCleanHooks()

        return outputs

    def getArgsDict(self, message):
        # front-end input is not guaranteed to be in dictionary format
        return message if isinstance(message, dict) else {'message': message}

    def init(self, stream, message, sid):  # pylint: disable=unused-argument
        self.argsDict = self.getArgsDict(message)
        context = self._getContext(message)
        args = self.loadComponentArguments(self.argsDict)
        context.update(args=args, sid=sid)
        return context


class SIOStreamHandler(Handler):
    def run(self, stream, message, sid, iostream, *arg, **kwargs):
        self.callBeforeInitHooks()
        context = self.init(stream, message, sid, iostream)
        self.callAfterInitHooks(context)

        self.callBeforeCallHooks(context)
        if not self.runFunc:
            raise error.ComponentHandlerNotSet()
        if not callable(self.runFunc):
            raise error.ComponentHandlerNotCallable(self.name)
        results = self.runFunc(stream, context, *arg, **kwargs)
        self.callAfterCallHooks(context)

        self.callBeforeSaveHooks(context)
        outputs = self.save(results, message=message)
        self.callAfterSaveHooks(context)

        self.callBeforeCleanHooks(context)
        self.clean()
        self.callAfterCleanHooks()

        return outputs

    def init(self, stream, message, sid, iostream):  # pylint: disable=unused-argument
        self.argsDict = self.getArgsDict(message)
        context = self._getContext(message)
        args = self.loadComponentArguments(self.argsDict)
        context.update(args=args, sid=sid, stream=iostream)
        return context
