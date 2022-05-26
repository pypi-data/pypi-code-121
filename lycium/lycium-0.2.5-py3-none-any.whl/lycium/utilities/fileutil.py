#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-
import json


def readJson(fileName):
    inJson = open(fileName, 'r')
    data = json.load(inJson)
    inJson.close()
    return data


def writeJson(fileName, data):
    outJson = open(fileName, 'w')
    outJson.write(json.dumps(data))
