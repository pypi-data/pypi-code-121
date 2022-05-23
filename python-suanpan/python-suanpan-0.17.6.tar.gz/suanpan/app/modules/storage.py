# coding=utf-8
from __future__ import absolute_import, print_function

import os

from suanpan import error
from suanpan import path as spath
from suanpan.app import app
from suanpan.app.modules.base import Module
from suanpan.storage import storage

module = Module()


@module.stream("storage.create")
def createStorage(context):
    args = context.args
    if not args.key:
        raise error.AppStorageModuleError("key is required")
    stream = context.stream
    stream.pipe(debugpath(args.key))
    if stream.done:
        upload(args.key)


@module.on("storage.download")
def downloadStrorage(context):
    args = context.args
    if not args.key:
        raise error.AppStorageModuleError("key is required")
    download(args.key)


@module.on("storage.upload")
def uploadStrorage(context):
    args = context.args
    if not args.key:
        raise error.AppStorageModuleError("key is required")
    upload(args.key)


@module.on("storage.remove")
def removeStrorage(context):
    args = context.args
    if not args.key:
        raise error.AppStorageModuleError("key is required")
    remove(args.key)


@module.on("storage.copy")
def copyStrorage(context):
    args = context.args
    if not args.src:
        raise error.AppStorageModuleError("src is required")
    if not args.dist:
        raise error.AppStorageModuleError("dist is required")
    copy(args.src, args.dist)


@module.on("storage.list")
def listStorage(context):
    args = context.args
    if not args.key:
        raise error.AppStorageModuleError("key is required")
    return [meta(key) for key in storage.listFiles(args.key)]


@module.on("storage.meta.get")
def getStorageMeta(context):
    args = context.args
    if not args.key:
        raise error.AppStorageModuleError("key is required")
    return meta(args.key)


@module.fn
def notifyMeta(key):
    app.sio.emit("storage.meta.notify", meta(key))


@module.fn
def meta(key):
    file = debugpath(key)
    mtime = os.path.getmtime(file) if os.path.exists(file) else None
    return {"src": f"debug/{key}", "key": key, "mtime": mtime}


@module.fn
def notify(data):
    app.sio.emit("storage.notify", data)


@module.fn
def download(key):
    notify({"key": key, "state": "downloading"})
    path = storage.download(
        key,
        debugpath(key),
        progress=lambda p: notify(
            {"key": key, "state": "downloading", "progress": p.progress}
        ),
    )
    notify({"key": key, "state": "downloaded"})
    notifyMeta(key)
    return path


@module.fn
def upload(key):
    notify({"key": key, "state": "uploading"})
    path = storage.upload(
        key,
        debugpath(key),
        progress=lambda p: notify(
            {"key": key, "state": "uploading", "progress": p.progress}
        ),
    )
    notify({"key": key, "state": "uploaded"})
    return path


@module.fn
def copy(src, dist):
    notify({"src": src, "dist": dist, "state": "copying"})
    storage.copy(
        src,
        dist,
        progress=lambda p: notify(
            {"src": src, "dist": dist, "state": "copying", "progress": p.progress}
        ),
    )
    notify({"src": src, "dist": dist, "state": "copied"})
    return dist


@module.fn
def remove(key):
    notify({"key": key, "state": "removing"})
    spath.remove(debugpath(key))
    storage.remove(
        key,
        progress=lambda p: notify(
            {"key": key, "state": "removing", "progress": p.progress}
        ),
    )
    notify({"key": key, "state": "removed"})
    return key


@module.fn
def debugpath(key):
    return app.sio.static("debug", key)
