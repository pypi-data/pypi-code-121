#!/usr/bin/python
""" misc utility functions """
import array

# python crc32c implementation
poly = 0x82F63B78
table = array.array('L')

for byte in range(256):
    crc = 0
    for bit in range(8):
        if (byte ^ crc) & 1:
            crc = (crc >> 1) ^ poly
        else:
            crc >>= 1
        byte >>= 1
    table.append(crc)

def crc32c(blob):
    value = 0xffffffff
    for b in blob:
        value = table[(int(b) ^ value) & 0xff] ^ (value >> 8)
    return 0xffffffff - value
