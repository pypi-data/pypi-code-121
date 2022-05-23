hidden_alphabet = '\u200B\u200C\u200D\u202F'
hidden_alphabet_table = {
    '\u200B': 0,
    '\u200C': 1,
    '\u200D': 2,
    '\u202F': 3,
}


def encode_byte(b):
    r = ''
    for _ in range(4):
        r = r + hidden_alphabet[b % 4]
        b //= 4
    return r


def decode_hidden_byte(h: str):
    b = 0
    for i, hb in enumerate(h):
        b |= (hidden_alphabet_table[hb] << i * 2)
    return b


def encode(ss: str):
    r = ''
    for b in ss.encode('ascii'):
        r = r + encode_byte(b)
    return r


def decode(ss: str):
    r = bytearray()
    for b in range(len(ss) // 4):
        r.append(decode_hidden_byte(ss[b * 4:b * 4 + 4]))
    return r.decode('ascii')
