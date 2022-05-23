# coding=utf-8
from __future__ import absolute_import, print_function

import os

import suanpan
from suanpan import api
from suanpan.app import app
from suanpan.app.arguments import String
from suanpan.utils import json


@app.param(String(key="app", required=True))
@app.param(String(key="graph", default=os.path.join("tmp", "graph")))
def SPAppGraphUpload(context):
    args = context.args
    filepath = (
        args.graph
        if args.graph.endswith(".json")
        else os.path.join(args.graph, f"{args.app}.json")
    )
    api.app.updateAppGraph(args.app, json.load(filepath))


if __name__ == "__main__":
    suanpan.run(app)
