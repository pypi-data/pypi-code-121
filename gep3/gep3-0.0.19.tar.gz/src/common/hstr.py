"""hstr.py

Generic functions working on strings containing only
    '0', '1', '2', '3', '4', '5', '6', '7', '8', '9',
    'A', 'B', 'C', 'D', 'E', 'F', 'a', 'b', 'c', 'd', 'e', 'f',
    and '_' characters
"""

# Standard library imports

# Third party imports

# Local application imports
from common.str import clean as _clean

def clean(hstr_in: str, command_name='()', hstr_name='') -> str:
    """clean(hstr)

    - Capitalizes hexadecimal digits
    - Removes '_' characters
    - Raises exceptions on illegal characters
    """
    return _clean(hstr_in, '0123456789ABCDEFabcdef', '_', command_name, hstr_name).upper()

def to_bitstr(hstr: str, command_name='()', hstr_name='') -> str:
    """to_bitstr(hstr): converts 'hex strings' to 'bit strings'
    """
    bstr = ''

    for nibble in clean(hstr, command_name, hstr_name):
        bstr += F"{int(nibble, 16):04b}"

    return bstr

def or_(hstr_a: str, hstr_b: str, command_name='()', hstr_name='') -> str:
    """or_(hstr_a, hstr_b):
    """
    hstr_a = clean(hstr_a, command_name, hstr_name)
    hstr_b = clean(hstr_b, command_name, hstr_name)
    length = max(len(hstr_a), len(hstr_b))
    hstr_a = hstr_a.rjust(length, '0')
    hstr_b = hstr_b.rjust(length, '0')
    or_hstr = ''

    for (nibble_a, nibble_b) in zip(hstr_a, hstr_b):
        or_hstr += F"{int(nibble_a, 16)|int(nibble_b, 16):X}"

    return or_hstr

def xor(hstr_a: str, hstr_b: str, command_name='()', hstr_name='') -> str:
    """xor(hstr_a, hstr_b):
    """
    hstr_a = clean(hstr_a, command_name, hstr_name)
    hstr_b = clean(hstr_b, command_name, hstr_name)
    length = max(len(hstr_a), len(hstr_b))
    hstr_a = hstr_a.rjust(length, '0')
    hstr_b = hstr_b.rjust(length, '0')
    xor_hstr = ''

    for (nibble_a, nibble_b) in zip(hstr_a, hstr_b):
        xor_hstr += F"{int(nibble_a, 16)^int(nibble_b, 16):X}"

    return xor_hstr

def and_(hstr_a: str, hstr_b: str, command_name='()', hstr_name='') -> str:
    """and_(hstr_a, hstr_b):
    """
    hstr_a = clean(hstr_a, command_name, hstr_name)
    hstr_b = clean(hstr_b, command_name, hstr_name)
    length = max(len(hstr_a), len(hstr_b))
    hstr_a = hstr_a.rjust(length, '0')
    hstr_b = hstr_b.rjust(length, '0')
    and_hstr = ''

    for (nibble_a, nibble_b) in zip(hstr_a, hstr_b):
        and_hstr += F"{int(nibble_a, 16)&int(nibble_b, 16):X}"

    return and_hstr

def not_(hstr_in: str, command_name='()', hstr_name='') -> str:
    """not(hstr):
    """
    hstr_in = clean(hstr_in, command_name, hstr_name)
    hstr_out = ''

    for nibble in hstr_in:
        hstr_out += xor(nibble, 'F')

    return hstr_out


def to_dec(hstr: str, command_name='()', hstr_name='') -> int:
    """to_dec():
    """
    return int(clean(hstr, command_name, hstr_name), 16)


def to_intlist(hstr: str, command_name='()', hstr_name='') -> list[int]:
    """to_intlist():
    """
    hstr = clean(hstr, command_name, hstr_name)
    if (len(hstr) % 2) != 0:
        raise ValueError(
            F"{command_name}: uneven length for {hstr_name}: {len(hstr)}")

    bytelist = []
    for i in range(len(hstr)//2):
        bytelist.append(int(hstr[i*2:(i+1)*2], 16))

    return bytelist


def minimum(hstr_a: str, hstr_b: str) -> str:
    """minimum():
    """
    hstr_a = clean(hstr_a)
    hstr_b = clean(hstr_b)

    if int(hstr_a, 16) == min(int(hstr_a, 16), int(hstr_b, 16)):
        return hstr_a

    return hstr_b

def split_by_length(hstr:str, length:int) -> list[str]:
    """split_by(): 
    """
    if len(hstr) % length != 0:
        # Error if the string is not a multiple of the length divider
        return []
    
    nr_splits = len(hstr)//length

    return [hstr[i*length:(i+1)*length] for i in range(nr_splits)]

def dscan_decimalize(hstr: str) -> str:
    """dscan_decimalize(): double scan decimalization
    """
    dstr1 = ''
    dstr2 = ''
    for h in clean(hstr):
        if h.isdigit():
            dstr1 = dstr1 + h
        else:
            dstr2 = dstr2 + F"{int(h, 16)-10}"

    return dstr1 + dstr2
