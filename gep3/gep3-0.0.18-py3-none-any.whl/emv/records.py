"""records.py
"""

# Standard library imports

# Third party imports

# Local application imports
from common import hstr as _hstr

def decode_afl(AFL:str):
    """decode_afl(): 
    """
    AFL = _hstr.clean(AFL)
    if len(AFL) % 8 != 0:
        # Error if the AFL is not a multiple of 4 bytes
        return None, "AFL is not a multiple of 4 bytes"
    
    afl = []
    for afl_element in _hstr.split_by_length(AFL, 8):
        r, err = _decode_afl_element(afl_element)
        if err is not None:
            return None, err
        else:
            afl.append(r)
    
    return afl, None

#
# Helper functions (assume a clean 'hstr' as input)
#


def _decode_afl_element(e:str):
    (byte1, byte2, byte3, byte4) = _hstr.split_by_length(e, 2)

    if _hstr.and_(byte1, '07') != '00':
        # Error if three least  significant bits are not zeroes
        return None, "AFL Byte 1, bits 3–1 not zeroes"

    SFI = int(byte1, 16)//8

    if byte2 == '00':
        # Error if the second byte is zero
        return None, "AFL Byte 2 is zero"
    first_record = int(byte2, 16)
    
    last_record = int(byte3, 16)
    if last_record < first_record:
        # Error if the last record is smaller than the first record
        return None, "AFL Byte 3 is smaller than Byte 2"
    
    oda_records = int(byte4, 16)
    if oda_records > (last_record - first_record + 1):
        # Error if the number of records used for ODA is greater than the total number of records
        return None, "AFL Byte 4 is greater than total number of records"
    
    return (SFI, first_record, last_record, oda_records), None