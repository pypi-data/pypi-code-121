#!/usr/bin/env python
# coding=utf-8

"""
Version: 0.1
Autor: zmf96
Email: zmf96@qq.com
Date: 2022-03-02 17:34:50
LastEditors: zmf96
LastEditTime: 2022-05-25 21:20:51
FilePath: /hotfinger/finger_handle_tools/hotfinge2csv.py
Description: 
"""
import csv
import json

hotfinger = []

with open("../data/hotfinger_v3.json", "r") as f:
    hotfinger = json.load(f)
with open("../data/hotfinger_v3.csv", "w") as f:
    writer = csv.writer(f, delimiter=",")
    keys = ["id", "name", "tags"]
    writer.writerow(keys)
    for item in hotfinger:
        writer.writerow([item["_id"]["$oid"], item["name"], ",".join(item["tags"])])
