# coding=utf-8
from __future__ import absolute_import, print_function

from suanpan.app import app
from suanpan.app.modules.base import Module
from suanpan.utils import image

module = Module()


@module.fn
def saveDebugImageAndNotify(img, itype):
    saveDebugImage(img, itype)
    notifyImageMeta({"type": itype})


@module.fn
def saveDebugImage(img, itype):
    image.save(app.sio.static("debug", f"{itype}.jpg"), img)


@module.fn
def notifyImageMeta(meta):
    app.sio.emit("images.meta.notify", meta)


@module.on("images.meta.get")
def getImageMeta(context):
    args = context.args
    return {
        "type": args.type,
        "src": f"debug/{args.type}.jpg",
    }
