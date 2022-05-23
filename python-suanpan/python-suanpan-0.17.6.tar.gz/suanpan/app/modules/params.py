# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app import app
from suanpan.app.modules.base import Module

module = Module()


@module.on("connect")
def notifyParamsConfigs(context):
    app.sio.emit("params.configs.notify", getParamsConfigs(context))
    app.sio.emit("params.notify", getParams(context))


@module.on("params.configs.get")
def getParamsConfigs(_):
    configs = app.sio._loop.options.params.configs  # pylint: disable=protected-access
    stream = app._stream  # pylint: disable=protected-access
    return {
        "title": configs.title or stream.title,
        "params": configs.params or [arg.paramConfigs for arg in stream.ARGUMENTS],
    }


@module.on("params.get")
def getParams(_):
    stream = app._stream  # pylint: disable=protected-access
    return stream.getParams()


@module.on("params.update")
def updateParams(context):
    return update(context.args, retry=True)


@module.fn
def update(args, retry=True):
    stream = app._stream  # pylint: disable=protected-access
    loop = app._loop  # pylint: disable=protected-access
    params = stream.updateParams(args)
    if retry:
        loop.retryLastMessage()
    params = stream.saveParams(params)
    return params
