#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import sys
import pkgutil
import shutil

# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3/28154841
import repackage
repackage.up()

import bridge_utils.xin2pbn.xin2pbn as xin2pbn
import bridge_utils.pbn2html.pbn2html as pbn2html

from bridge_utils.mdbridge.lin2pbn import bbo2pbn

import requests
import re

from string import Template

def wrapper(str):
    #print(str)
    wrapper="""
```{=latex}
%s
```
""" % str.strip()
    return wrapper

auction_template=r"""\begin{quote}
	\begin{bidding}
		$auction
	\end{bidding}
\end{quote}
"""

board_template=r"""\begin{quote}
	\crdima
    {\begin{minipage}[t]{\br}$ul\end{minipage}}
    {\begin{minipage}[t]{\br}$ll\end{minipage}}
    {$north}
    {$west}
    {$east}
    {$south}
    {\begin{minipage}[t]{\br}$ur\end{minipage}}
\end{quote}
"""

pbn={}

def hands_parse(deal):
    # deal=.xxxx..xxx&.94.A.AKT7&-&.AKQ6.865.
    # hands = {
    #    'W': {'S': '8 2', 'H': 'J 10 8', 'D': '10 9 7 4', 'C': 'J 10 5 3'}, 
    #    'N': {'S': 'x J 3', 'H': '9 4', 'D': 'A J', 'C': 'A K Q 8 7 4'}, 
    #    'E': {'S': '10 9 6 4', 'H': '7 5 3 2', 'D': 'K Q 2', 'C': '9 6'}, 
    #    'S': {'S': '无 Q 7 5','H': 'A K Q 6', 'D': '8 6 5 3', 'C': '2'}
    #}
    allhands = deal.split("&")
    wnes = []
    for hand in allhands:
        shdc = []
        if hand == "-":
            shdc = ["S","K","I","P"]
        else:
            shdc = [" ".join(i) for i in hand.split(".")]
            shdc = [x.replace('T', '10') for x in shdc]
            shdc = [x if x != "" else "—" for x in shdc]

        zip_iterator = zip(['S','H','D','C'], shdc)
        wnes.append(dict(zip_iterator))
        #print(wnes)
    zip_iterator = zip(['W','N','E','S'], wnes)
    hands = dict(zip_iterator)
    return hands #"\hand{}{94}{A}{AK87}"

def bidding_parse(auction):
    return(auction)

def latex_suit(suit):
    # c => 
    for word, initial in {"S":"♠", "H":"♥","D":"♦","C":"♣" }.items():
        suit = suit.replace(word, initial)
    return suit

def pbn_latex_auction(pbn):
    src = Template(auction_template)
    # Pass \> 2NT\> Pass \> 3\c\\
    # Pass \> 3NT\> Pass \> 6NT\\
    # All Pass
    # need insert empty cell based on auction
    auction = pbn["tags"]["Auction"]
    section_auction = pbn["section_auction"]

    position="WNES" 
    empty_cells = position.index(auction)

    # handle ==1==, 6D?, 6D!
    filtered_auction = [x for x in section_auction.split() if not x.startswith("=")]
    # print(filtered_auction)
    table = ""
    col = 0
    for empty in range(empty_cells):
        table += " \\>"
        col += 1
    for one in filtered_auction:
        # print("aution:", one)
        one = one.replace("!", '')
        table +="%s " % latex_suit(one)
        if col == 3:
            col = 0
            table += "\\\\\n"
        else:
            col += 1
            table += "\\>"
    all = { "auction": table}
    return src.safe_substitute(all)

def latex_info(info,bottom=False):
    if bottom:
        # easiest way to put into bottom with extra newline &, totally for 4 lines
        for i in range(3 - info.count('&')):
            info="\hfill\\\\" + info
    info = info.replace("&","\\\\")  # line break with \\
        
    return info

def latex_card(cards):
    # 'W': {'S': '8 2', 'H': 'J 10 8', 'D': '10 9 7 4', 'C': 'J 10 5 3'}, 
    str = "\hand{%s}{%s}{%s}{%s}" % (cards["S"].replace(" ", ""), cards["H"].replace(" ", ""),cards["D"].replace(" ", ""),cards["C"].replace(" ", ""))
    return str #"\hand{}{94}{A}{AK87}"

def pbn_latex_deal(pbn, cards="NESW", ll="", ul="", ur=""):
    all = {}
    tags = pbn["tags"]
    hands = pbn["hands"]
    empty_hand = "\\nonhand{ }{ }{ }{ }"
    # print(hands["N"])

    all["north"] = latex_card(hands["N"])
    all["west"] = latex_card(hands["W"])
    all["east"] = latex_card(hands["E"])
    all["south"] = latex_card(hands["S"])
    for card in "NESW":
        if card not in cards:
            if card == "N":
                # all["north"] = empty_hand
                # use space can hide the cell
                all["north"] = ""
            if card == "W":
                all["west"] = empty_hand
            if card == "E":
                all["east"] = empty_hand
            if card == "S":
                #all["south"] = empty_hand
                # use space can hide the cell
                all["south"] = ""

    if ul == "":
        all["ul"] = latex_info("Dealer: " + tags["Dealer"] + "\\\\" + "Vul: " + tags["Vulnerable"])
    else:
        all["ul"] = latex_info(ul)
    all["ll"] = latex_info(ll, bottom=True)
    all["ur"] = latex_info(ur)

    src = Template(board_template)
    #template = open("deal_template.html", "r", encoding="utf-8").read()
    #src = Template(template
    # print(all)
    result = src.safe_substitute(all)
    return result

def convert(block):
    global pbn
    PBN_FILE="interesting"
    result = ""
    for line in block:
        #print(line)
        if line.startswith("http"):
            # print("heelo:", line)
            if "DealLog" in line: # xinrui
                xin2pbn.xin2pbn(line, PBN_FILE)
                pbn = pbn2html.get_from_pbn_file(PBN_FILE+".pbn")
                # print(pbn)
            elif "bridgebase" in line: # bbo lin format
                bbo2pbn(line, PBN_FILE+".pbn")
                pbn=pbn2html.get_from_pbn_file(PBN_FILE+".pbn")
            else:
                continue
            # print(pbn)
        elif line.startswith("auction"):
            # handle part later to change pbn
            newpbn=pbn.copy()
            kv = line.split("=")
            if len(kv) > 1:
                auction=kv[1]
                #print(newpbn["hands"])
                newpbn["section_auction"] = bidding_parse(auction)
            result += wrapper(pbn_latex_auction(newpbn))
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
            result += wrapper(pbn_latex_deal(newpbn, cards=cards, ll=ll,ul=ul, ur=ur))
    return result

def process_md(md_file):
    output = os.path.splitext(md_file)[0]+'.bridge-tex'
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

def download_sample():
    if __name__ == '__main__':
        print("dear contributor, do this in package mode")
        return
    sample_files=['ramsey.md', 'meta.txt']
    for sample_file in sample_files:
        if os.path.exists(sample_file):
            print("%s already exists, ingore (or remove it first)" % sample_file)
        else:
            print("download sample file -> [%s]" % sample_file)
            shutil.copy(os.path.join(os.path.dirname(os.path.realpath(__file__)),sample_file),".")

def main():
    if len(sys.argv) > 1:
        params = sys.argv[1:]
        if params[0] == "sample":
            download_sample()
        else:
            for md in sys.argv[1:]:
                process_md(md)

if __name__ == '__main__':
    main()