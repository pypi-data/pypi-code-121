import hashlib

b58 = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def base58_encode(n):
    result = ''
    while n > 0:
        result = b58[n % 58] + result
        n //= 58
    return result


def base58_decode(s):
    result = 0
    for i in range(0, len(s)):
        result = result * 58 + b58.index(s[i])
    return result


def base256_encode(n):
    result = b''
    while n > 0:
        result = bytes([n % 256]) + result
        n //= 256
    return result


def base256_decode(s):
    result = 0
    for c in s:
        result = result * 256 + c
    return result


def count_leading_chars(s, ch):
    count = 0
    for c in s:
        if c == ch:
            count += 1
        else:
            break
    return count


# https://en.bitcoin.it/wiki/Base58Check_encoding
def base58_check_encode(payload, version_byte=0):
    s = bytes([version_byte]) + payload
    checksum = hashlib.sha256(hashlib.sha256(s).digest()).digest()[0:4]
    result = s + checksum
    leading_zeros = count_leading_chars(result, 0)
    return '1' * leading_zeros + base58_encode(base256_decode(result))


def base58_check_decode(s):
    leading_ones = count_leading_chars(s, '1')
    s = base256_encode(base58_decode(s))
    result = b'\0' * leading_ones + s[:-4]
    chk = s[-4:]
    checksum = hashlib.sha256(hashlib.sha256(result).digest()).digest()[0:4]
    assert(chk == checksum)
    return result[1:], result[0]


def reverse_hex(s):
    return bytes.fromhex(s)[::-1].hex()
