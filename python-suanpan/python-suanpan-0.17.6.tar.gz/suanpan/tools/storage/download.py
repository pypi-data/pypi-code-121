# coding=utf-8
from __future__ import absolute_import, print_function

import suanpan
from suanpan.app import app
from suanpan.arguments import String
from suanpan.storage import storage


@app.param(String(key="local", required=True))
@app.param(String(key="remote", required=True))
def SPStorageDownload(context):
    args = context.args
    storage.download(args.remote, args.local)


if __name__ == "__main__":
    suanpan.run(app)
