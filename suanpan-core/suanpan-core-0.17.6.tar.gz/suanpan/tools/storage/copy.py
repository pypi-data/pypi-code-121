# coding=utf-8
from __future__ import absolute_import, print_function

import suanpan
from suanpan.app import app
from suanpan.app.arguments import String
from suanpan.storage import storage


@app.param(String(key="src", required=True))
@app.param(String(key="dist", required=True))
def SPStorageCopy(context):
    args = context.args
    storage.copy(args.src, args.dist)


if __name__ == "__main__":
    suanpan.run(app)
