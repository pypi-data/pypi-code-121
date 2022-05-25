#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import sys
import pkgutil

# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3/28154841
import repackage
repackage.up()

import bridge_utils.xin2pbn.xin2pbn as xin2pbn
import bridge_utils.pbn2html.pbn2html as pbn2html

def wrapper(str):
    wrapper="""
```{=html}
%s
```
""" % str
    return wrapper

pbn={}

def hands_parse(deal):
    # deal=.xxxx..xxx&.94.A.AKT7&-&.AKQ6.865.
    hands = {
        'W': {'S': '8 2', 'H': 'J 10 8', 'D': '10 9 7 4', 'C': 'J 10 5 3'}, 
        'N': {'S': 'x J 3', 'H': '9 4', 'D': 'A J', 'C': 'A K Q 8 7 4'}, 
        'E': {'S': '10 9 6 4', 'H': '7 5 3 2', 'D': 'K Q 2', 'C': '9 6'}, 
        'S': {'S': '无 Q 7 5','H': 'A K Q 6', 'D': '8 6 5 3', 'C': '2'}
    }
    allhands = deal.split("&")
    wnes = []
    for hand in allhands:
        shdc = []
        if hand == "-":
            shdc = ["无","关","紧","要"]
        else:
            shdc = [" ".join(i) for i in hand.split(".")]
            shdc = [x.replace('T', '10') for x in shdc]
            shdc = [x if x != "" else "—" for x in shdc]

        zip_iterator = zip(['S','H','D','C'], shdc)
        wnes.append(dict(zip_iterator))
        #print(wnes)
    zip_iterator = zip(['W','N','E','S'], wnes)
    hands = dict(zip_iterator)
    return hands

def convert(block):
    global pbn
    PBN_FILE="interesting"
    result = ""
    for line in block:
        #print(line)
        if line.startswith("http"):
            xin2pbn.xin2pbn(line, PBN_FILE)
            pbn = pbn2html.get_from_pbn_file(PBN_FILE+".pbn")
        elif line.startswith("auction"):
            result += wrapper(pbn2html.pbn_html_auction(pbn))
        elif line.startswith("deal"):
            options = line.strip().split("|")
            cards = "NEWS"
            ll = ul = ur = ""
            newpbn=pbn.copy()
            for option in options:
                if option.startswith("deal"):
                    # handle part later to change pbn
                    kv = option.split("=")
                    if len(kv) > 1:
                        deal=kv[1]
                        #print(newpbn["hands"])
                        newpbn["hands"] = hands_parse(deal)
                else:
                    key,value = option.split("=")
                    if key=="cards":
                        cards = value
                    elif key == "ll": # lower left
                        ll = value.strip('\"')
                    elif key == "ul":
                        ul = value.strip('\"')
                    elif key == "ur":
                        ur = value.strip('\"')
            result += wrapper(pbn2html.pbn_html_deal(newpbn, cards=cards, ll=ll,ul=ul, ur=ur))
    return result

def process_md(md_file):
    output = os.path.splitext(md_file)[0]+'.bridge'
    print("processing %s -> %s" % (md_file, output))

    with io.open(output, "w", encoding="utf-8") as md_target:
        with io.open(md_file, encoding="utf-8") as md_orig:
            block = []
            found = False

            for line in md_orig.readlines():
                if found:
                    if line.strip() == "</pre>":
                        #print("come here", block)
                        result = convert(block)
                        md_target.write(result)
                        found = False
                    else:
                        block.append(line)
                else:
                    if line.rstrip() == '<pre lang="bridge">':
                        found = True
                        block = []
                    else:
                        md_target.write(line)

def main():
    for md in sys.argv[1:]:
        process_md(md)

if __name__ == '__main__':
    main()