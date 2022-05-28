from collections import deque


def base10_to_base36(number):
    character = '0123456789abcdefghijklmnopqrstuvwxyz'
    if number:
        rn = deque()
        while number:
            number, i = divmod(number, 36)
            rn.appendleft(character[i])
        return ''.join(rn)
    return '0'

def percent_to_float(text):
    ''' percent_to_float('3.5%') -> 0.035 '''
    if '%' in text:
        return float(text.replace('%', '')) / 100
    return float(text)
