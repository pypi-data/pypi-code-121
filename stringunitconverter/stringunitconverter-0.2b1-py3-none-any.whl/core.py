"""
2022, March 12
"""

import importlib_resources as ir
import json


# Load JSON files in dictionaries for fast access
# see https://importlib-resources.readthedocs.io/en/latest/using.html
def getdict(filename: str) -> dict:
    source = ir.files('stringunitconverter').joinpath(filename)
    with ir.as_file(source) as filepath:
        with open(filepath, 'r') as f:
            a = json.load(f)
    return a


prefixes = getdict('prefixes.json')
units = getdict('units.json')

operators_and_brackets = frozenset(('*', '/', '^', '-', '+', '(', ')', ' ',
                                    '·', '.'))
digits = frozenset(('0', '1', '2', '3', '4', '5', '6', '7', '8', '9'))
nonunits = operators_and_brackets.union(digits)


def multiplier(a: str, b: str, *args, **kwargs) -> float:
    """
    :param a: input unit
    :param b: output unit
    :return: multiplier
    """
    return get_factor(a, *args, **kwargs) / get_factor(b, *args, **kwargs)


def get_factor(a: str, unsafe=False) -> float:
    """
    :param a: input unit
    :param unsafe: set to 'True' to disable protection against malicious code
    :return: multiplier
    """
    # Replace each hat with two asterisks
    # and replace multiplication dot with asterisk
    # and replace ² and ³ with **2 and **3 respectively
    for i in range(len(a)-1, -1, -1):
        if a[i] == '^':
            a = a[:i] + '**' + a[i+1:]
        elif a[i] == '·':
            a = a[:i] + '*' + a[i+1:]
        elif a[i] == '²':
            a = a[:i] + '**2' + a[i+1:]
        elif a[i] == '³':
            a = a[:i] + '**3' + a[i+1:]

    # Replace every unit-with-prefix with its appropriate multiplier
    # iterate over input string from back to front
    # `ks` = start index, `ke` = end index
    ke = len(a) - 1
    while True:
        # Search for end index `ke`
        # character in known non-units -> nothing to replace -> skip these indices
        while ke > -1 and a[ke] in nonunits:
            ke -= 1
        # found end of unit string on index `ke`
        # or if before start of the string, end processing
        if ke < 0:
            break
        # Search for start index `ks`
        ks = ke
        while ks > -1 and a[ks] not in nonunits:
            ks -= 1
        # found start of unit string on index `ke + 1`
        # Extract the string and replace it
        detected_unit_string = a[ks+1:ke+1]
        #print('  detected_unit_string: <' + detected_unit_string + '>')
        #print('  ks:', ks, ', ke:', ke)
        # Substitute
        a = a[:ks+1] + unit_to_factor_string(detected_unit_string) + a[ke+1:]
        # If at start of the string, end processing
        if ks < 0:
            break
        # If space between two units, replace it with a multiplier
        if ks > 0 and a[ks] == ' ' and a[ks-1] not in operators_and_brackets:
            a = a[:ks] + '*' + a[ks+1:]
        # Move end index to start index
        ke = ks
    # Before evaluating the string, search for suspicious code,
    # unless unsafe mode has been enabled
    if unsafe is False:
        if 'import' in a or 'eval' in a:
            raise Exception('The string may not contain "import" or "eval". ' +
                            'Add argument "unsafe=True" to circumvent protection.')
    # Evaluate string
    a = eval(a)
    # Return outcome
    return a


def unit_to_factor_string(a: str) -> str:
    """
    Convert string with a single unit and prefix, e.g. 'kPa',
    to its multiplier string, e.g. '(1e3*1)'.

    :param a: single unit
    :return: multiplier
    """
    # assume no prefix
    if a in units:
        return units[a]
    # doesn't work, so assume prefix and split it
    p = a[0]
    u = a[1:]
    if p in prefixes and u in units:
        return '(' + prefixes[p] + '*' + units[u] + ')'
    # neither of the two worked, so error out
    print('Failed to decode string: <' + a + '>')
    return a


if __name__ == '__main__':
    pass
