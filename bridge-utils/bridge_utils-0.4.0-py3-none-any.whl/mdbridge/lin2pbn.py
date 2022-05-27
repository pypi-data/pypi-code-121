#!/usr/bin/env python
# -*- coding: utf-8 -*-
import os
import io
import sys
import pkgutil

import requests
import re

from string import Template
from collections import deque

def numToDirection(n):
    return ['S', 'W', 'N', 'E'][n%4]

# this code copied from https://github.com/kevinywlui/lin2pbn/blob/master/lin2pbn.py
# http://www.himbuv.com/nieuw/english/lin_en
# https://github.com/morgoth/lin/blob/master/lib/lin/parser.rb
def lin2pbn(linstring, pbnfile):
    linList = linstring.split('||')

    # Extract Players SWNE
    [south, west, north, east] = linList[0].split('|')[1].split(',')

    # Extract hands
    dd = linList[1].split('|')[1].split(',')
    hands = [list(map(lambda x: x[::-1], re.split('S|H|D|C', d))) for d in dd]
    [dealerIndex, _, _, _] = [x.pop(0) for x in hands]
    
    dealerIndex = int(dealerIndex)
    dealer = numToDirection(dealerIndex -1)
    if len(hands[3]) == 0:
        rank = 'AKQJT98765432'
        hands[3] = 4 * ['']
        for i in range(4):
            for j in range(13):
                if all([rank[j] not in hands[k][i] for k in range(3)]):
                    hands[3][i] = hands[3][i] + rank[j]
    # hands always starts from S now, so need rotate
    # hands.rotate(dealerIndex -1)
    for _ in range(dealerIndex -1):
        hands.append(hands.pop(0))
    # print(hands)
    deal = dealer + ":" + " ".join([".".join(x) for x in hands])

    # Extract auction
    aa = linList[2].split('|')[1::2]
    board = aa[0].split(' ')[1]
    if aa[1] == 'o':
        vulnerable = 'None'
    elif aa[1] == 'e':
        vulnerable = 'ES'
    elif aa[1] == 'n':
        vulnerable = 'NS'
    else:
        vulnerable = 'All'

    bids = aa[2::]
    bids = ['Pass' if x == 'p' else x for x in bids]
    auction = ''
    for i in range(len(bids) // 4):
        t = ['', '', '', '']
        for j in range(4):
            if 4 * i + j < len(bids):
                t[j] = bids[4 * i + j]
        auction = auction + '{0[0]:<7}{0[1]:<7}{0[2]:<7}{0[3]:<7}\n'.format(t)

    stake = ''
    for x in bids[::-1]:
        if x == 'XX':
            stake = 'XX'
            continue
        if x == 'X' and stake != 'XX':
            stake = 'X'
            continue
        if x[1] in ['S', 'H', 'C', 'D', 'N']:
            contract = x + stake
            strain = x[1:]
            break

    for x in bids:
        if x[1:] == strain:
            declarerIndex = bids.index(x)
            break
    declarer = ['S', 'W', 'N', 'E'][(declarerIndex+dealerIndex - 1) % 4]

    # Extract play
    pp = linList[3::]
    pp = [p.split('|')[1::2] for p in pp]
    if pp[-1] == []:
        claim = 0
    else:
        claim = pp[-1][-1] 
    
    play = ''
    for x in pp:
        if x == []:
            continue
        t = ['', '', '', '']
        for j in range(len(x)):
            t[j] = x[j]
        play = play + '{0[0]:<4}{0[1]:<4}{0[2]:<4}{0[3]:<4}\n'.format(t)
    play = [numToDirection(declarerIndex+1),play]

    PBNString = ''
    PBNString = PBNString + '[Event \"\"]\n'
    PBNString = PBNString + '[Site \"\"]\n'
    PBNString = PBNString + '[Date \"\"]\n'
    PBNString = PBNString + '[Board \"{}\"]\n'.format(board)
    PBNString = PBNString + '[West \"{}\"]\n'.format(west)
    PBNString = PBNString + '[North \"{}\"]\n'.format(north)
    PBNString = PBNString + '[East \"{}\"]\n'.format(east)
    PBNString = PBNString + '[South \"{}\"]\n'.format(south)
    PBNString = PBNString + '[Dealer \"{}\"]\n'.format(dealer)
    PBNString = PBNString + '[Vulnerable \"{}\"]\n'.format(vulnerable)
    PBNString = PBNString + '[Deal \"{}\"]\n'.format(deal)
    PBNString = PBNString + '[Scoring \"\"]\n'
    PBNString = PBNString + '[Declarer \"{}\"]\n'.format(declarer)
    PBNString = PBNString + '[Contract \"{}\"]\n'.format(contract)
    PBNString = PBNString + '[Result \"\"]\n'
    PBNString = PBNString + '[Auction \"{}\"]\n{}'.format(dealer, auction)
    PBNString = PBNString + '[Play \"{0[0]}\"]\n{0[1]}'.format(play)
    with io.open(pbnfile, "w", encoding="utf-8") as text_file:
        print("write to file %s" % pbnfile)
        text_file.write(PBNString)

def bbo2pbn(url, pbnfile):
        # URL of the image to be downloaded is defined as image_url 
    r = requests.get(url) # create HTTP response object 
    lin_str = r.text
    print("Download from %s and lin is:\n%s" % (url, lin_str))
    lin2pbn(lin_str, pbnfile)

def main():
#  https://www.bridgebase.com/myhands/fetchlin.php?id=775620181&when_played=1610708401
    # pn|precisionb,Que10plm,Jansty,Rollo100|st||md|2S7TJH289JQAD2C59A,S9H7D489JQKC3468Q,S248QAH5KD36TC7JK,|rh||ah|Board 4|sv|b|mb|p|mb|1S|mb|p|mb|2H|mb|p|mb|p|mb|p|pg||pc|DK|pc|D3|pc|D5|pc|D2|pg||pc|DQ|pc|D6|pc|D7|pc|H2|pg||pc|H8|pc|H7|pc|HK|pc|H3|pg||pc|H5|pc|H4|pc|HJ|pc|D4|pg||pc|HQ|pc|S9|pc|C7|pc|H6|pg||pc|HA|pc|C3|pc|DT|pc|HT|pg||pc|SJ|pc|D8|pc|S2|pc|SK|pg||pc|DA|pc|H9|pc|D9|pc|S4|pg||pc|CA|pc|C4|pc|CJ|pc|C2|pg||pc|ST|pc|C6|pc|S8|pc|S3|pg||mc|11|
    # |md|2S7TJH289JQAD2C59A,S9H7D489JQKC3468Q,S248QAH5KD36TC7JK,
    # [Deal "W:JT7.AQJ982.2.A95 9.7.KQJ984.Q8643 AQ842.K5.T63.KJ7 K653.T643.A75.T2"]
    # [Deal "W:9.7.KQJ984.Q8643 AQ842.K5.T63.KJ7 K653.T643.A75.T2 JT7.AQJ982.2.A95"]
    if len(sys.argv) > 1:
        url = sys.argv[1]
        pbnfile = "interesting.pbn"
        if "bridgebase" in url:
            bbo2pbn(url, pbnfile)
        else:
            lin2pbn(lin_str, pbnfile)
    else:
        print("lin2pbn linstr|bbo")

if __name__ == '__main__':
    main()