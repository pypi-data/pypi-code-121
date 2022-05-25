"""commands.py
"""

# Standard library imports

# Third party imports

# Local application imports
from common.ber import encode_length as length
from common.ber import encode


def SELECT(aid: str) -> dict:
    """SELECT(): generate APDU for SELECT command
    """
    known_aid_list = {'MASTERCARD' : 'A0000000041010', 'MAESTRO' : 'A00000000410103060', 'VISA' : 'A0000000031010'}
    return {'header' : '00A40400', 'data' : known_aid_list.get(aid, aid), 'Le' : '00'}

def GET_PROCESSING_OPTIONS(pdol: str = '') -> dict:
    """GET_PROCESSING_OPTIONS(): generate APDU for GET PROCESSING OPTIONS command
    """
    return {'header' : '80A80000', 'data' : encode('83', pdol), 'Le' : '00'}

def GPO(pdol: str) -> dict:
    """GPO(): generate APDU for GET PROCESSING OPTIONS command
    """
    return GET_PROCESSING_OPTIONS(pdol)

def READ_RECORD(SFI:int, record:int) -> dict:
    """READ_RECORD(): generate APDU for READ RECORD command
    """
    return {'CLA' : '00', 'INS' : 'B2', 'P1' : F"{record:02X}", 'P2' : F"{SFI*8+4:02X}", 'Le' : '00'}

def GET_DATA(tag: str) -> dict:
    """GET_DATA: generate APDU for GET DATA command
    """
    return {'header' : '80CA' + tag, 'Le' : '00'}