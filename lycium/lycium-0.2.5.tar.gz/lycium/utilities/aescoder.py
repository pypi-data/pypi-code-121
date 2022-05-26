#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-

import base64
from Crypto.Cipher import AES

# Padding for the input string --not
# related to encryption itself.
BLOCK_SIZE = 16  # Bytes
pkcs5_pad = lambda s: s + (BLOCK_SIZE - len(s) % BLOCK_SIZE) * \
                chr(BLOCK_SIZE - len(s) % BLOCK_SIZE)
pkcs5_unpad = lambda s: s[:-ord(s[len(s) - 1:])]

def aes_encode(text, dk, iv, encrypt_mode=AES.MODE_CBC):
    cryptor = AES.new(str(dk).encode('utf-8'), encrypt_mode, str(iv).encode('utf-8'))
    raw = pkcs5_pad(text)
    result = cryptor.encrypt(raw.encode('utf-8'))
    resultbase64 = base64.b64encode(result).decode()
    return resultbase64

def aes_decode(text, dk, iv, encrypt_mode=AES.MODE_CBC):
    enc = base64.b64decode(text)
    cryptor = AES.new(str(dk).encode('utf-8'), encrypt_mode, str(iv).encode('utf-8'))
    result = pkcs5_unpad(cryptor.decrypt(enc)).decode('utf8')
    return result

def aes_encode_no_base64(text, dk, iv, encrypt_mode=AES.MODE_CBC):
    cryptor = AES.new(str(dk).encode('utf-8'), encrypt_mode, str(iv).encode('utf-8'))
    raw = pkcs5_pad(text)
    result = cryptor.encrypt(raw.encode('utf-8'))
    return str(result)[2:-1]    # directly convert bytes to str contains b'...', so remove it.
