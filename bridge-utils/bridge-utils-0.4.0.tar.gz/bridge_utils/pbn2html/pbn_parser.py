"""
Code for parsing PBN files borrowed from alorenzen/DoubleDummy
https://github.com/alorenzen/DoubleDummy/blob/master/pbn_parser.py
which comes from
http://4coder.org/python-source-code/18/pybridge-0.3.0/pybridge/bridge/pbn.py.html
"""
import os
from .game_state import *
#from game_state import *


class ParseError(Exception):
    """Raised when PBN parser encounters an unexpected input."""

def importPBN(pbn):
    SUIT = 'SHDC'
    CARDRANK = dict(zip('23456789TJQKA',range(2,15)))
    POSITION = dict(zip('NESW',Player.POSITION))
    PLAYERINDEX = dict(zip('NESW',range(1,5)))
    tags, sections, notes = parsePBN(pbn)
    # try to fetch lead
    if "Play" in sections:
        # it could be empty or ""
        playlist = sections["Play"].split()
        if len(playlist):
            tags["Lead"] = sections["Play"].split()[0]
        else:
            tags["Lead"] = ""
    else:
        tags["Lead"] = ""
    if "Event" not in tags:
        tags["Event"] = ""
    #print(tags,sections, notes)
    if 'Deal' not in tags:
        raise ParseError("Required tag 'Deal' not found")
    first, cards = tags['Deal'].split(":")
    index = PLAYERINDEX[first.strip()] - 1
    #print(PLAYERINDEX)
    #print(POSITION)
    #print(Player.POSITION)
    order = Player.POSITION[index:] + Player.POSITION[:index]
    # print(first,cards,index, order)
    hands = {}
    for player, hand in zip(order, cards.strip().split()):
        # print("loop:", player,hand)
        hands[player] = {}
        for suit, suitcards in zip(SUIT, hand.split('.')):
            hands[player][suit] = ""
            for rank in suitcards:
                card = Card(suit,CARDRANK[rank])
                if hands[player][suit] != "":
                    hands[player][suit] += " "
                if rank == "T":
                    rank ="10"
                hands[player][suit] += rank
            if hands[player][suit] == "":
                hands[player][suit] = "—"
    #print(hands)
    #print((sections['Optimumresulttable'].split('\n'))[1:20])
    #results = filter(lambda x: x[1] == 'NT',map(lambda x: x.strip().split(),sections['Optimumresulttable'].split('\n'))[1:20])
    #expected = {}
    #for player, suit, tricks in results:
    #    player = POSITION[player]
    #    deal = Deal(hands,player)
    #    if not deal.isValidDeal():
    #        raise ParseError("Deal does not validate")
    #    expected[player] = (deal,tricks)
    return tags, hands, sections["Auction"]

def parsePBN(pbn):
    """Parses the given PBN string and extracts:
    
      * for each PBN tag, a dict of associated key/value pairs.
      * for each data section, a dict of key/data pairs.
        
    This method does not interpret the PBN string itself.
    
    @param pbn: a string containing PBN markup.
    @return: a tuple (tag values, section data, notes).
    """
    tagValues, sectionData, notes = {}, {}, {}
    tag = 'Default Tag'
    for line in pbn.splitlines():
        line.strip()  # Remove whitespace.

        if line.startswith('%'):  # A comment.
            pass  # Skip over comments.

        elif line.startswith('['):  # A tag.
            line = line.strip('[]')  # Remove leading [ and trailing ].
            # The key is the first word, the value is everything after.
            tag, value = line.split(' ', 1)
            tag = tag.capitalize()
            value = value.strip('\'\"')
            if tag == 'Note':
                notes.setdefault(tag, [])
                notes[tag].append(value)
            else:
                tagValues[tag] = value

        else:  # Line follows tag, add line to data buffer for section.
            sectionData.setdefault(tag, '')
            sectionData[tag] += line + '\n'

    return tagValues, sectionData, notes


def testImport():
    pbnstr = file("pbn_files/OptimumResultTable.pbn").read()
    g = importPBN(pbnstr)
    return g
