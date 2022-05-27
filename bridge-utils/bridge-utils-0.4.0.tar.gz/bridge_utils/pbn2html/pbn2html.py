#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import sys
import pkgutil
from pkgutil import iter_modules

import pkg_resources  # part of setuptools
version = pkg_resources.require("bridge-utils")[0].version

# https://stackoverflow.com/questions/16981921/relative-imports-in-python-3/28154841
import repackage
repackage.up()

from bridge_utils.pbn2html.pbn_parser import importPBN, ParseError
#from pbn_parser import importPBN, ParseError

from string import Template

try:
    from ddstable import ddstable
except ImportError as error:
    pass

def module_exists(module_name):
    return module_name in (name for loader, name, ispkg in iter_modules())

language="Chinese"

html_template="""
<!DOCTYPE html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="Generator" content="pbn2html toolkit">
    <title>Enjoy the bridge game</title>
  </head>
  <h2>Introduction</h2>
  <p>this is designed to be used (copy/paste) for HTML/Microsoft Word</p>
  <p>Designed by Larry Cai and produced by <a href="https://pypi.org/project/bridge-utils/">bridge-utils/pbn2html</a>, version $version</p>
  <p>Credit to <a href="https://bridgecomposer.com/">BridgeComposer Version 5.83 (64 bit)</a></p>
  <body class=bcbody>
    <!-- Credit to BridgeComposer Version 5.83 (64 bit) - https://bridgecomposer.com/ -->
    <div class=bcboard style="text-align: center">
        $all
    </div>
  </body>
</html>
"""
card_template="""
              <table class=bchand style="border-collapse: collapse; border-spacing: 0">
                <tr class=bchand>
                  <td class=bcpip style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0; width: 1em; text-align: center"><span class=bcspades style="color: black">&spades;</span></td>
                  <td class=bchand style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0">$spade</td>
                </tr>
                <tr class=bchand>
                  <td class=bcpip style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0; width: 1em; text-align: center"><span class=bchearts style="color: red">&hearts;</span></td>
                  <td class=bchand style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0">$heart</td>
                </tr>
                <tr class=bchand>
                  <td class=bcpip style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0; width: 1em; text-align: center"><span class=bcdiams style="color: red">&diams;</span></td>
                  <td class=bchand style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0">$diamond</td>
                </tr>
                <tr class=bchand>
                  <td class=bcpip style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0; width: 1em; text-align: center"><span class=bcclubs style="color: black">&clubs;</span></td>
                  <td class=bchand style="font: 10pt Verdana, sans-serif; padding: 1px; padding-top: 0; padding-bottom: 0">$club</td>
                </tr>
              </table>
"""

card_empty_template="""
    <table class=bchand style="border-collapse: collapse; border-spacing: 0">
    </table>
"""

board_template="""
              <table class=bcct style="width: 4em; height: 4em; border-collapse: collapse; font: 10pt simsun, sans-serif; color: #ffffff; border: 1px solid #aaaaaa">
                <tr class=bcct1>
                  <td class=bcct1 style="text-align: center; vertical-align: text-top; padding: 1px"></td>
                  <td class=bcct1 style="text-align: center; vertical-align: text-top; padding: 1px;background-color: $ns_vulnerable;">N</td>
                  <td class=bcct1 style="text-align: center; vertical-align: text-top; padding: 1px"></td>
                </tr>
                <tr class=bcct2>
                  <td class=bcct2a style="text-align: left; vertical-align: text-top; padding: 1px; background-color: $ew_vulnerable;">W</td>
                  <td class=bcct2b style="text-align: center; padding: 1px; color: black;">$dealer</td>
                  <td class=bcct2c style="text-align: right; vertical-align: text-top; padding: 1px; background-color: $ew_vulnerable;">E</td>
                </tr>
                <tr class=bcct3>
                  <td class=bcct3 style="text-align: center; vertical-align: text-top; padding: 1px"></td>
                  <td class=bcct3 style="text-align: center; vertical-align: text-top; padding: 1px; background-color: $ns_vulnerable;">S</td>
                  <td class=bcct3 style="text-align: center; vertical-align: text-top; padding: 1px"></td>
                </tr>
              </table>
"""
extra_template="""
            <td class=bchd3 style="padding: 1px; font: 10pt Verdana, sans-serif; padding: 1px; text-align: left; vertical-align: top;">
                $contract by $declarer<br />Lead: $lead
            </td>
"""

info_template="""
            <td class=bchd3 style="padding: 1px; font: 10pt Verdana, sans-serif; padding: 1px; text-align: left; vertical-align: $valign;">$info</td>
"""

auction_template="""
          $auction
"""

pbn_template="""
<table style="border: 1px solid;font-size:small;" cellspacing="0px" cellpadding="0px" align="right" bgcolor="#F8F8F8">
    <tbody>
      <tr bgcolor="#FFFFFF">
        <td style="border-style: none;"></td>
        <td style="border-style: none;" align="center"><small>&nbsp;<font color="black">&clubs;</font>&nbsp;</small></td>
        <td style="border-style: none;" align="center"><small>&nbsp;<font color="red">&diams;</font>&nbsp;</small></td>
        <td style="border-style: none;" align="center"><small>&nbsp;<font color="red">&hearts;</font>&nbsp;</small></td>
        <td style="border-style: none;" align="center"><small>&nbsp;<font color="black">&spades;</font>&nbsp;</small></td>
        <td style="border-style: none;" align="center"><small><font color="black">NT</font></small></td>
      </tr>
      $tr
    </tbody>
  </table>
"""

def read_template(template_file):
    # read local first (debug), then module
    try:
        template = open(template_file, "r",encoding="utf-8").read()
        src = Template(template)
    except FileNotFoundError:
        if __name__ == "__main__":
            raise IOError("can't find file, debug?")
        else:
            template = pkgutil.get_data(__name__,template_file)
            src = Template(template.decode('utf-8'))
    return src

def html_card(cards):
    src = Template(card_template)
    all = {
        "spade" : cards["S"],
        "heart" : cards["H"],
        "diamond" : cards["D"],
        "club" : cards["C"]
    }
    return src.safe_substitute(all)

def html_board(vulnerable, dealer):
    arrows={"S": "&darr;","W": "&larr;","N": "&uarr;","E": "&rarr;"}
    src = Template(board_template)
    
    NONE_COLOR="#93C47D"
    VULNERABLE_COLOR="#E06666"

    all = {}
    if vulnerable == "NS":
        all["ns_vulnerable"]= VULNERABLE_COLOR
        all["ew_vulnerable"]= NONE_COLOR
    elif vulnerable == "EW":
        all["ew_vulnerable"]= VULNERABLE_COLOR
        all["ns_vulnerable"]= NONE_COLOR
    elif vulnerable.upper() == "NONE":
        all["ew_vulnerable"]= NONE_COLOR
        all["ns_vulnerable"]= NONE_COLOR
    else:
        all["ew_vulnerable"]= VULNERABLE_COLOR
        all["ns_vulnerable"]= VULNERABLE_COLOR
    all["dealer"] = arrows[dealer]
    
    return src.safe_substitute(all)

def bid_css(contract):
    rank = contract[0]
    suit = contract[1:]
    css = rank
    space="<span style='font: 10pt Times, serif'>&thinsp;</span>"
    suit_css = {
        'S':  space + "<span class=bcspades style='color:black;font: 10pt Verdana, sans-serif;'>&spades;</span>",
        "H":  space + "<span class=bchearts style='color: red; font: 10pt Verdana, sans-serif;'>&hearts;</span>",
        "D":  space + "<span class=bcdiams style='color: red; font: 10pt Verdana, sans-serif;'>&diams;</span>",
        "C":  space + "<span class=bcclubs style='color:black;font: 10pt Verdana, sans-serif;'>&clubs;</span>",
        "NT": space + "NT",
    }
    if contract in [ "AP", "Pass", "X", "XX" ]:
        css = contract
    else:
        css += suit_css[suit]
    return css

def contract_css(contract):
    rank = contract[0]
    suit = double = ""
    x = contract.find("X")
    if x == -1: # no x or xx
        suit = contract[1:]
    else:
        suit = contract[1:x]
        double = contract[x:]
    css = rank
    space="<span style='font: 10pt Times, serif'>&thinsp;</span>"
    suit_css = {
        'S':  space + "<span class=bcspades style='color:black;font: 10pt Verdana, sans-serif;'>&spades;</span>",
        "H":  space + "<span class=bchearts style='color: red; font: 10pt Verdana, sans-serif;'>&hearts;</span>",
        "D":  space + "<span class=bcdiams style='color: red; font: 10pt Verdana, sans-serif;'>&diams;</span>",
        "C":  space + "<span class=bcclubs style='color:black;font: 10pt Verdana, sans-serif;'>&clubs;</span>",
        "NT": space + "NT",
    }
    css += suit_css[suit] + double.lower()

    return css

def html_extra(contract, declarer,lead):
    src = Template(extra_template)
    css = contract_css(contract)
    # trans_declarer={"S": "南","W": "西","N": "北","E": "东"}
    # trans_declarer={"S": "S","W": "W","N": "N","E": "E"}
    suit_css = {
        'S':  "<span class=bcspades style='color:black;font: 10pt Verdana, sans-serif;'>&spades;</span>",
        "H":  "<span class=bchearts style='color: red; font: 10pt Verdana, sans-serif;'>&hearts;</span>",
        "D":  "<span class=bcdiams style='color: red; font: 10pt Verdana, sans-serif;'>&diams;</span>",
        "C":  "<span class=bcclubs style='color:black;font: 10pt Verdana, sans-serif;'>&clubs;</span>"
    }
    trans_declarer={"S": "South","W": "West","N": "North","E": "East"}
    all = { "declarer": trans_declarer[declarer], "contract" : css, "lead" : suit_css[lead[0]] + lead[1]}
    return src.safe_substitute(all)

def html_info(info, bottom=False):
    src = Template(info_template)
    info = info.replace("&","<br />")
    if bottom:
        valign = "bottom"
    else:
        valign = "top"
    all = { "info": info, "valign" : valign}
    return src.safe_substitute(all)

def html_auction(auction, section_auction):
    src = Template(auction_template)
    # need insert empty cell based on auction
    position="WNES" 
    empty_cells = position.index(auction)

    # handle ==1==, 6D?, 6D!
    filtered_auction = [x for x in section_auction.split() if not x.startswith("=")]
    # print(filtered_auction)
    css = "<tr class=bcauction>"
    col = 0
    for empty in range(empty_cells):
        css += "<td class=bcauction style='padding: 1px; text-align: left; white-space: nowrap'></td>\n"
        col += 1
    for one in filtered_auction:
        # print("aution:", one)
        one = one.replace("!", '').replace("?","")
        css +="<td class=bcauction style='padding: 1px; text-align: left; white-space: nowrap'>%s</td>\n" %  bid_css(one)
        if col == 3:
            col = 0
            css += "</tr>\n"
        else:
            col += 1
    css += "</tr>\n"
    all = { "auction": css}
    return src.safe_substitute(all)


def html_pbn(pbn):
    tables = ddstable.get_ddstable(pbn)
    src = Template(pbn_template)
    tr = ""
    card_suit=["C", "D", "H", "S", "NT"]
    for each in tables.keys():
        td = ""
        for suit in card_suit:
            trick=tables[each][suit]
            trick_str = "-"
            if trick > 6:
                trick_str = str(trick-6)
            td += "<td style='border-style: none;' align='center'>%s</td>\n" % trick_str
        tr += "<tr><td style='border-style: none;' align='center'><font color='#008080'>%s</font></td>\n%s</tr>" % ( each, td)
    all = { "tr": tr}
    return src.safe_substitute(all)
    
def pbn2html(pbn_file):
    all = {
        "generated" : "2021-05-14"
    }

    # handle multiple pbn in one file
    pbnstr = open(pbn_file,encoding="utf-8" ).read()
    # delimiter="[Event"
    delimiter="\n*"
    if len(pbnstr.split(delimiter)) > 1:
        pbns =  [e for e in pbnstr.split(delimiter) if "Declarer" in e]
    else:
        delimiter="[Event" # old format used for larry
        pbns =  [delimiter+e for e in pbnstr.split(delimiter) if "Deal" in e]
    print("found", len(pbns), "boards")
    result = ""
    #print(pbns)
    for pbn in pbns:
        # print("==================================", pbn)
        try:
            tags, hands, section_auction = importPBN(pbn)
            #print(tags, hands,section_auction)
            all["title"] = tags["Event"]
            all["north"] = html_card(hands["N"])
            all["west"] = html_card(hands["W"])
            all["east"] = html_card(hands["E"])
            all["south"] = html_card(hands["S"])
            all["board"] = html_board(tags["Vulnerable"],tags["Dealer"])
            all["extra"] = html_extra(tags["Contract"],tags["Declarer"],tags["Lead"])
            all["auction"] = html_auction(tags["Auction"], section_auction)
            src = read_template("template.html")
            result += src.safe_substitute(all)
        except ParseError as error:
            print(error)
        except KeyError as kerror:
            print("Key error: ", kerror)

        #print(len(result))
    src = Template(html_template)
    all = { "all": result, "version": version }
    result = src.safe_substitute(all)
    # output = os.path.splitext(pbn_file)[0]+'.html'
    output = pbn_file + '.html'
    with io.open(output, "w", encoding="utf-8") as text_file:
        print("write to file %s" % output)
        text_file.write(result)

def get_from_pbn(pbn):
    tags, hands, section_auction = importPBN(pbn)
    pbn = {
        "tags": tags,
        "hands": hands,
        "section_auction" : section_auction
    }
    # print(hands)
    return pbn

def get_from_pbn_file(pbn_file):
    pbn = open(pbn_file,encoding="utf-8" ).read()
    return get_from_pbn(pbn)

def pbn_html_auction(pbn):
    all = {}
    tags = pbn["tags"]
    section_auction = pbn["section_auction"]
    all["auction"] = html_auction(tags["Auction"], section_auction)
    template = pkgutil.get_data(__name__,'auction_template.html')
    src = Template(template.decode('utf-8'))
    result = src.safe_substitute(all)
    return result

def pbn_html_deal(pbn, cards="NESW", ll="", ul="", ur="", dds=False):
    all = {}
    tags = pbn["tags"]
    hands = pbn["hands"]
    empty_hand = card_empty_template
    # print(hands["N"])

    all["north"] = html_card(hands["N"])
    all["west"] = html_card(hands["W"])
    all["east"] = html_card(hands["E"])
    all["south"] = html_card(hands["S"])
    for card in "NESW":
        if card not in cards:
            if card == "N":
                all["north"] = empty_hand
            if card == "W":
                all["west"] = empty_hand
            if card == "E":
                all["east"] = empty_hand
            if card == "S":
                all["south"] = empty_hand

    if dds and module_exists("ddstable"):
        PBN = bytes(pbn["tags"]["Deal"],encoding="raw_unicode_escape")
        # print(PBN)
        all["lr"] = html_pbn(PBN)
    else:
        all["lr"] = ""

    all["board"] = html_board(tags["Vulnerable"],tags["Dealer"])
    if ul == "":
        all["ul"] = html_extra(tags["Contract"],tags["Declarer"],tags["Lead"])
    else:
        all["ul"] = html_info(ul)
    all["ll"] = html_info(ll, bottom=True)
    all["ur"] = html_info(ur)

    src = read_template('deal_template.html')
    #template = open("deal_template.html", "r", encoding="utf-8").read()
    #src = Template(template)
    result = src.safe_substitute(all)
    return result

def pbn_html_all(pbn):
    all = {}
    tags = pbn["tags"]
    hands = pbn["hands"]
    section_auction = pbn["section_auction"]
    all["north"] = html_card(hands["N"])
    all["west"] = html_card(hands["W"])
    all["east"] = html_card(hands["E"])
    all["south"] = html_card(hands["S"])
    all["board"] = html_board(tags["Vulnerable"],tags["Dealer"])
    all["extra"] = html_extra(tags["Contract"],tags["Declarer"],tags["Lead"])
    all["auction"] = html_auction(tags["Auction"], section_auction)
    template = pkgutil.get_data(__name__,'all_template.html')
    src = Template(template.decode('utf-8'))
    result = src.safe_substitute(all)
    return result

def main():
    # print(sys.argv)
    if len(sys.argv) > 1:
        param = sys.argv[1:]
        if param[0].endswith(".pbn"):
            pbn2html(param[0])
            pbn = get_from_pbn_file(param[0])
            #print(pbn_html_all(pbn))
            #print(pbn_html_auction(pbn))
            
            pbn_html_deal(pbn, cards="NS", dds=True)
            #print(pbn_html_deal(pbn, cards="EW"))
            #print(pbn_html_deal(pbn, cards="NEWS"))
            #print(pbn_html_deal(pbn, ul=" ", ur="群组赛1209&牌号 4/8", ll="NS 4/12&EW 0"))
        else:
            print("pbn2html.py <file.pbn>")
    else:
        print("pbn2html.py <file.pbn>")

if __name__ == '__main__':
    main()

