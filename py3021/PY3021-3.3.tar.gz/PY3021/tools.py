# -*- coding: utf-8 -*-

def str_to_hex(s):
    import binascii
    return binascii.b2a_hex(s.encode())
if __name__ == '__main__':
    print(str_to_hex('hello'))