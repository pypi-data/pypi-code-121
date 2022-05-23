# coding=utf-8
from __future__ import absolute_import, print_function

import atexit
import base64
import functools
import itertools
import re
import signal
import sys

from suanpan import g
from suanpan.arguments import Bool
from suanpan.log import logger
from suanpan.objects import HasName


class HasArguments(object):
    GLOBAL_ARGUMENTS = []
    ARGUMENTS = []

    @classmethod
    def dictFromList(cls, l):
        return dict(zip(l[0::2], l[1::2]))

    @classmethod
    def listFromDict(cls, d):
        return list(itertools.chain(*d.items()))

    @classmethod
    def getArgsDict(cls, *args, **kwargs):
        argDict = {}
        argDict.update(cls.getArgsDictFromEnv())
        argDict.update(cls.getArgsDictFromCli())
        argDict.update(cls.getArgsDictFromList(args))
        argDict.update(cls.getArgsDictFromDict(kwargs))
        return {key: value for key, value in argDict.items() if value != ""}

    @classmethod
    def getArgsDictFromCli(cls):
        argv = sys.argv[1:]
        return cls.getArgsDictFromList(argv)

    @classmethod
    def getArgsDictFromEnv(cls):
        argStringBase64 = g.appParams
        logger.debug(f"SP_PARAM(Base64)='{argStringBase64}'")
        try:
            argString = base64.b64decode(argStringBase64).decode()
        except Exception:  # pylint: disable=broad-except
            argString = argStringBase64  # temporary fix for SP_PARAM(Base64)
        logger.debug(f"SP_PARAM='{argString}'")
        regex = r"(--[\w-]+)\s+(?:(?P<quote>[\"\'])(.*?)(?P=quote)|([^\'\"\s]+))"
        groups = re.findall(regex, argString, flags=re.S)
        argv = list(
            itertools.chain(*[(group[0], group[-2] or group[-1]) for group in groups])
        )
        return cls.getArgsDictFromList(argv)

    @classmethod
    def getArgsDictFromList(cls, l):
        return cls.getArgsDictFromDict(cls.dictFromList(l))

    @classmethod
    def getArgsDictFromDict(cls, d):
        return {key.lstrip("-"): value for key, value in d.items()}

    def loadFormatArguments(self, arguments, argsDict):
        for arg in arguments:
            arg.load(argsDict).format()
        return arguments

    def loadCleanArguments(self, arguments, argsDict):
        for arg in arguments:
            arg.load(argsDict).clean()
        return arguments

    def saveArguments(self, arguments, results):
        return {
            argument.key: argument.save(result)
            for argument, result in zip(arguments, results)
        }

    def resetArguments(self, arguments):
        for arg in arguments:
            arg.reset()
        return arguments

    def getArguments(self, *args, **kwargs):
        raise NotImplementedError("Method not implemented!")

    def getGlobalArguments(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.GLOBAL_ARGUMENTS

    def getComponentArguments(self, *args, **kwargs):  # pylint: disable=unused-argument
        return self.ARGUMENTS

    @classmethod
    def defaultArgumentsFormat(cls, argsDict, arguments):
        return {
            cls._defaultArgumentKeyFormat(arg.key): getattr(argsDict, arg.key, None)
            for arg in arguments
        }

    @classmethod
    def _defaultArgumentKeyFormat(cls, key):
        return cls._toCamelCase(cls._removePrefix(key))

    @classmethod
    def _removePrefix(cls, string, delimiter="-", num=1):
        pieces = string.split(delimiter)
        pieces = pieces[num:] if len(pieces) > num else pieces
        return delimiter.join(pieces)

    @classmethod
    def _toCamelCase(cls, string, delimiter="-"):
        camelCaseUpper = lambda i, s: s[0].upper() + s[1:] if i and s else s
        return "".join(
            [camelCaseUpper(i, s) for i, s in enumerate(string.split(delimiter))]
        )

    @classmethod
    def argumentsDict(cls, arguments):
        result = {}
        for arg in arguments:
            keys = (arg.key, arg.alias)
            result.update({key: arg.value for key in keys if key})
        return result

    @classmethod
    def getArgumentValueFromDict(cls, data, arg):
        value = data.get(arg.alias)
        if value is not None:
            return value

        value = data.get(arg.key)
        if value is not None:
            return value

        return None

    @classmethod
    def hasArgumentValueFromDict(cls, data, arg):
        return arg.alias in data or arg.key in data


class HasLogger(HasName):
    def __init__(self):
        super().__init__()

    @property
    def logger(self):
        return logger


class HasDevMode(HasArguments):
    DEV_ARGUMENTS = [Bool(key="debug", default=False)]

    def getGlobalArguments(self, *args, **kwargs):
        arguments = super().getGlobalArguments(*args, **kwargs)
        return arguments + self.DEV_ARGUMENTS


class HasInitHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeInitHooks = getattr(self, "beforeInitHooks", [])
        self.afterInitHooks = getattr(self, "afterInitHooks", [])

    def beforeInit(self, *args, **kwargs):
        pass

    def callBeforeInitHooks(self, *args, **kwargs):
        self.beforeInit(*args, **kwargs)
        for hook in self.beforeInitHooks:
            hook(*args, **kwargs)

    def addBeforeInitHooks(self, *hooks):
        self.beforeInitHooks.extend(hooks)
        return self

    def afterInit(self, *args, **kwargs):
        pass

    def callAfterInitHooks(self, *args, **kwargs):
        self.afterInit(*args, **kwargs)
        for hook in self.afterInitHooks:
            hook(*args, **kwargs)

    def addAfterInitHooks(self, *hooks):
        self.afterInitHooks.extend(hooks)
        return self


class HasSaveHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeSaveHooks = getattr(self, "beforeSaveHooks", [])
        self.afterSaveHooks = getattr(self, "afterSaveHooks", [])

    def beforeSave(self, *args, **kwargs):
        pass

    def callBeforeSaveHooks(self, *args, **kwargs):
        self.beforeSave(*args, **kwargs)
        for hook in self.beforeSaveHooks:
            hook(*args, **kwargs)

    def addBeforeSaveHooks(self, *hooks):
        self.beforeSaveHooks.extend(hooks)
        return self

    def afterSave(self, *args, **kwargs):
        pass

    def callAfterSaveHooks(self, *args, **kwargs):
        self.afterSave(*args, **kwargs)
        for hook in self.afterSaveHooks:
            hook(*args, **kwargs)

    def addAfterSaveHooks(self, *hooks):
        self.afterSaveHooks.extend(hooks)
        return self


class HasCleanHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeCleanHooks = getattr(self, "beforeCleanHooks", [])
        self.afterCleanHooks = getattr(self, "afterCleanHooks", [])

    def beforeClean(self, *args, **kwargs):
        pass

    def callBeforeCleanHooks(self, *args, **kwargs):
        self.beforeClean(*args, **kwargs)
        for hook in self.beforeCleanHooks:
            hook(*args, **kwargs)

    def addBeforeCleanHooks(self, *hooks):
        self.beforeCleanHooks.extend(hooks)
        return self

    def afterClean(self, *args, **kwargs):
        pass

    def callAfterCleanHooks(self, *args, **kwargs):
        self.afterClean(*args, **kwargs)
        for hook in self.afterCleanHooks:
            hook(*args, **kwargs)

    def addAfterCleanHooks(self, *hooks):
        self.afterCleanHooks.extend(hooks)
        return self


class HasCallHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeCallHooks = getattr(self, "beforeCallHooks", [])
        self.afterCallHooks = getattr(self, "afterCallHooks", [])

    def beforeCall(self, *args, **kwargs):
        pass

    def callBeforeCallHooks(self, *args, **kwargs):
        self.beforeCall(*args, **kwargs)
        for hook in self.beforeCallHooks:
            hook(*args, **kwargs)

    def addBeforeCallHooks(self, *hooks):
        self.beforeCallHooks.extend(hooks)
        return self

    def afterCall(self, *args, **kwargs):
        pass

    def callAfterCallHooks(self, *args, **kwargs):
        self.afterCall(*args, **kwargs)
        for hook in self.afterCallHooks:
            hook(*args, **kwargs)

    def addAfterCallHooks(self, *hooks):
        self.afterCallHooks.extend(hooks)
        return self


class HasLoopHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeLoopHooks = getattr(self, "beforeLoopHooks", [])
        self.afterLoopHooks = getattr(self, "afterLoopHooks", [])

    def beforeLoop(self, *args, **kwargs):
        pass

    def callBeforeLoopHooks(self, *args, **kwargs):
        self.beforeLoop(*args, **kwargs)
        for hook in self.beforeLoopHooks:
            hook(*args, **kwargs)

    def addBeforeLoopHooks(self, *hooks):
        self.beforeLoopHooks.extend(hooks)
        return self

    def afterLoop(self, *args, **kwargs):
        pass

    def callAfterLoopHooks(self, *args, **kwargs):
        self.afterLoop(*args, **kwargs)
        for hook in self.afterLoopHooks:
            hook(*args, **kwargs)

    def addAfterLoopHooks(self, *hooks):
        self.afterLoopHooks.extend(hooks)
        return self


class HasTriggerHooks(object):
    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeTriggerHooks = getattr(self, "beforeTriggerHooks", [])
        self.afterTriggerHooks = getattr(self, "afterTriggerHooks", [])

    def beforeTrigger(self, *args, **kwargs):
        pass

    def callBeforeTriggerHooks(self, *args, **kwargs):
        self.beforeTrigger(*args, **kwargs)
        for hook in self.beforeTriggerHooks:
            hook(*args, **kwargs)

    def addBeforeTriggerHooks(self, *hooks):
        self.beforeTriggerHooks.extend(hooks)
        return self

    def afterTrigger(self, *args, **kwargs):
        pass

    def callAfterTriggerHooks(self, *args, **kwargs):
        self.afterTrigger(*args, **kwargs)
        for hook in self.afterTriggerHooks:
            hook(*args, **kwargs)

    def addAfterTriggerHooks(self, *hooks):
        self.afterTriggerHooks.extend(hooks)
        return self


class HasExitHooks(object):
    if sys.platform == "win32":
        SIGNALS = (
            signal.SIGTERM,
            signal.SIGINT,
        )
    else:
        SIGNALS = (
            signal.SIGUSR1,
            signal.SIGTERM,
            signal.SIGQUIT,
            signal.SIGHUP,
            signal.SIGINT,
        )

    def __init__(self, *args, **kwargs):  # pylint: disable=unused-argument
        super().__init__()
        self.beforeExitHooks = getattr(self, "beforeExitHooks", [])

    def _exit(self, signum, frame):
        logger.debug(f"Signal Exit: {signum} {frame}")
        sys.exit(signum)

    def beforeExit(self, *args, **kwargs):
        pass

    def callBeforeExitHooks(self, *args, **kwargs):
        self.beforeExit(*args, **kwargs)
        for hook in self.beforeExitHooks:
            hook(*args, **kwargs)

    def addBeforeExitHooks(self, *hooks):
        self.beforeExitHooks.extend(hooks)
        return self

    def registerBeforeExitHooks(self, *args, **kwargs):
        atexit.register(self.callBeforeExitHooks, *args, **kwargs)
        for s in self.SIGNALS:
            signal.signal(s, self._exit)
        return self
