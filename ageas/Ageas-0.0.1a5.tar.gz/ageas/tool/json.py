#!/usr/bin/env python3
"""
JSON file related tools

author: jy, nkmtmsys
"""
import re
import gzip
import json

# to ouput data in json format
def encode(data, out = 'out.js', indent = 4):
    if re.search(r'\.gz$', out):
        with gzip.open(out, 'w+') as output:
            output.write(json.dumps(data).encode('utf-8'))
    else:
        with open(out, 'w+') as output:
            json.dump(data, output, indent = indent)

# to load in json file
def decode(file):
    if re.search(r'\.gz$', file):
        with gzip.open(file, 'r') as json_file:
            data = json.load(json_file)
        return data
    else:
        with open(file, 'r') as json_file: data = json.load(json_file)
        return data
