# coding=utf-8
from __future__ import absolute_import, print_function

import suanpan
from suanpan.app import app
from suanpan.app.arguments import String
from suanpan.dw import dw
from suanpan.utils import csv


@app.param(String(key="file", required=True))
@app.param(String(key="table", required=True))
def SPDWUpload(context):
    args = context.args
    dw.writeTable(args.table, csv.load(args.file))


if __name__ == "__main__":
    suanpan.run(app)
