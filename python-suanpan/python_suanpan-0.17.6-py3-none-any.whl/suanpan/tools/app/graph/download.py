# coding=utf-8
from __future__ import absolute_import, print_function

import os

import suanpan
from suanpan import api, path
from suanpan.app import app
from suanpan.app.arguments import String
from suanpan.utils import json


@app.param(String(key="app", required=True))
@app.param(String(key="dist", default=os.path.join("tmp", "graph")))
def SPAppGraphDownload(context):
    args = context.args
    filepath = (
        args.dist
        if args.dist.endswith(".json")
        else os.path.join(args.dist, f"{args.app}.json")
    )
    path.mkdirs(filepath, parent=True)
    json.dump(api.app.getAppGraph(args.app), filepath)


if __name__ == "__main__":
    suanpan.run(app)
