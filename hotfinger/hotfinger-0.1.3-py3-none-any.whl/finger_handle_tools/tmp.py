#!/usr/bin/env python
# coding=utf-8

"""
Version: 0.1
Autor: zmf96
Email: zmf96@qq.com
Date: 2022-02-24 10:41:55
LastEditors: zmf96
LastEditTime: 2022-02-24 10:53:12
FilePath: /hotfinger/data/tmp.py
Description: 
"""

import json

new_data = []
with open("./hotfinger.json", "r", encoding="utf-8") as f:
    data = json.load(f)
    for item in data:
        print(item["name"])
        new_item = {
            "_id": item["_id"],
            "name": item["name"],
            "content": {"/": item["value"]},
            "tags": ["tide"],
        }
        new_data.append(new_item)

with open("../data/tmp.json", "w", encoding="utf-8") as f:
    json.dump(new_data, f, indent=4, ensure_ascii=False)
