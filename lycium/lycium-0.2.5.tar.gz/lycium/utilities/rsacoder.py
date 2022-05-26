#!/usr/bin/env python3.6
#! -*- coding: utf-8 -*-

import rsa
from . import base64_encode

def rsa_encode(data, pubkey, format='PEM'):
    if isinstance(pubkey, str):
        pubkey = rsa.PublicKey.load_pkcs1(pubkey.encode(), format=format)
    elif isinstance(pubkey, bytes):
        pubkey = rsa.PublicKey.load_pkcs1(pubkey, format=format)
    enc_text = rsa.encrypt(data.encode(), pubkey)
    return base64_encode(enc_text)

def rsa_encode_ne(data, pubkeys):
    pubkey = rsa.PublicKey(pubkeys.get('n'), pubkeys.get('e'))
    enc_text = rsa.encrypt(data.encode(), pubkey)
    return base64_encode(enc_text)
