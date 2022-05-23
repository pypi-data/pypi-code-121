# coding=utf-8
from __future__ import absolute_import, print_function

import suanpan
from suanpan.app import app
from suanpan.app.arguments import String
from suanpan.storage import storage


@app.param(String(key="remote", required=True))
def SPStorageRemove(context):
    args = context.args
    storage.remove(args.remote)


if __name__ == "__main__":
    suanpan.run(app)
