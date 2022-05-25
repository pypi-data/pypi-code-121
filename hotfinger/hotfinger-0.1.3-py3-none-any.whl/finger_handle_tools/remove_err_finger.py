#!/usr/bin/env python
# coding=utf-8

"""
Version: 0.1
Autor: zmf96
Email: zmf96@qq.com
Date: 2022-03-02 08:15:49
LastEditors: zmf96
LastEditTime: 2022-03-02 09:06:48
FilePath: /hotfinger/finger_handle_tools/remove_err_finger.py
Description: 
"""
import json

ErrFingers = None
with open("../errfinger.json", "r") as f:
    ErrFingers = json.load(f)

HotFingersV1 = None
with open("../data/hotfinger_v1.json", "r") as f:
    HotFingersV1 = json.load(f)
HotFingersV2 = None
with open("../data/hotfinger_v2.json", "r") as f:
    HotFingersV2 = json.load(f)

hotfinger = []
# hotfinger.extend(HotFingersV1)
# hotfinger.extend(HotFingersV2)

with open("../data/hotfinger.json", "r") as f:
    hotfinger = json.load(f)
print(len(hotfinger))
for errf in ErrFingers:
    print(errf)
    for k in errf.keys():
        for item in hotfinger:
            if k == item["name"]:
                hotfinger.remove(item)

print(len(hotfinger))
with open("../data/hotfinger.json", "w", encoding="utf-8") as f:
    json.dump(hotfinger, f, indent=4, ensure_ascii=False)
