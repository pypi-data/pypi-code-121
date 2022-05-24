"""bitstr.py

Generic functions working on strings containing only '0', '1', and '_' characters
"""

# Standard library imports
import math as _math

# Third party imports

# Local application imports


def clean(bstr_in: str, command_name='()', bstr_name='') -> str:
    """clean():

    - Removes '_' characters
    - Raises exceptions on illegal characters
    """
    bstr_out = ''
    for bit in bstr_in:
        if bit in '01':
            bstr_out += bit
        elif bit in ' _':
            pass
        else:
            if bstr_name == '':
                raise TypeError(F"{command_name}: Unknown bit: {bit}")
            else:
                raise TypeError(
                    F"{command_name}: Unknown bit in {command_name}: {bit}")

    return bstr_out


def to_hstr(bstr: str, command_name='()', bstr_name='') -> str:
    """to_hstr():
    """
    bstr = clean(bstr, command_name, bstr_name)
    length = _math.ceil(len(bstr)/4)

    return F"{int(bstr, 2):X}".rjust(length, '0')


def xor(bstr_a: str, bstr_b: str, command_name='()', bstr_name='') -> str:
    """xor(bstr_a, bstr_b):
    """
    bstr_a = clean(bstr_a, command_name, bstr_name)
    bstr_b = clean(bstr_b, command_name, bstr_name)
    length = max(len(bstr_a), len(bstr_b))

    return F"{int(bstr_a, 2)^int(bstr_b, 2):b}".rjust(length, "0")
