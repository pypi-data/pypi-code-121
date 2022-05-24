#!/usr/bin/python
""" efi ucs-16 encoding and decoding """

class StringUCS16:
    """ class reprsenting an efi ucs16 string """

    def __init__(self, string = None):
        self.data = b''
        if string:
            self.parse_str(string)

    def parse_bin(self, data, offset):
        """ set StringUCS16 from bytes data, reads to terminating 0 """
        self.data = b''
        pos = offset
        while True:
            unichar = data[pos : pos + 2]
            if len(unichar) != 2 or unichar == b'\0\0':
                break
            self.data += unichar
            pos += 2

    def parse_str(self, string):
        """ set StringUCS16 from python string """
        self.data = string.encode('utf-16le')

    def __bytes__(self):
        """ return bytes representing StringUCS16, with termianting 0 """
        return self.data + b'\0\0'

    def size(self):
        """ number of bytes returned by bytes() """
        return len(self.data) + 2

    def __str__(self):
        return self.data.decode('utf-16le')

    def __repr__(self):
        return f"{self.__class__.__name__}('{str(self)}')"

def from_ucs16(data, offset):
    """ convert ucs-16 bytes to StringUCS16 """
    obj = StringUCS16()
    obj.parse_bin(data, offset)
    return obj

def from_string(string):
    """ convert python string to StringUCS16 """
    return StringUCS16(string)
