"""emv.py
"""

# Standard library imports

# Third party imports

# Local application imports
from pcsc import card
from emv import commands as command
from emv import records

def SELECT(card_service: card._CardService, aid: str, trace=None):
    return card.send_apdu(card_service, command.SELECT(aid), trace=trace)

def GPO(card_service: card._CardService, pdol: str, trace=None):
    return card.send_apdu(card_service, command.GPO(pdol), trace=trace)

def READ_RECORD(card_service: card._CardService, sfi: int, record:int, trace=None):
    return card.send_apdu(card_service, command.READ_RECORD(sfi, record), trace=trace)

def READ_RECORDs(card_service: card._CardService, AFL: str, trace=None):
    output = []

    for (sfi, first, last, _) in records.decode_afl(AFL):
        for n in range(first, last+1):
            r, err = READ_RECORD(card_service, sfi, n, trace=trace)
            output.append((r, err))
            if err != '':
                return output
    
    return output


def GET_DATA(card_service: card._CardService, tag: str, trace=None):
    return card.send_apdu(card_service, command.GET_DATA(tag), trace=trace)
