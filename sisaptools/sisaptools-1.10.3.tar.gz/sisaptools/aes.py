# -*- coding: utf8 -*-

"""
Encriptació i desencriptació amb AES.
La clau es guarda en un fitxer.
"""

import base64
import hashlib
import os

from Crypto.Cipher import AES
from Crypto import Random

from .constants import APP_CHARSET


class AESCipher(object):
    """
    Classe principal.
    """
    def __init__(self):
        """Captura la clau del fitxer (pot ser de qualsevol longitut)."""
        if 'AES_KEY' in os.environ:
            pth = os.environ['AES_KEY']
            key = open(pth).read()
        else:
            key = 'testkey'
        self.key = hashlib.sha256(AESCipher.str_to_bytes(key)).digest()
        self.bs = 32

    @staticmethod
    def str_to_bytes(data):
        """Converteix unicode a bytes."""
        u_type = type(b''.decode(APP_CHARSET))
        if isinstance(data, u_type):
            return data.encode(APP_CHARSET)
        return data

    def _pad(self, s):
        return s + (self.bs - len(s) % self.bs) * \
               AESCipher.str_to_bytes(chr(self.bs - len(s) % self.bs))

    @staticmethod
    def _unpad(s):
        return s[:-ord(s[len(s)-1:])]

    def encrypt(self, raw):
        """
        Funció per encriptar.
        Pot rebre unicode o bytes, i retorna unicode.
        """
        raw = self._pad(AESCipher.str_to_bytes(raw))
        iv = Random.new().read(AES.block_size)
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        return base64.b64encode(iv + cipher.encrypt(raw)).decode(APP_CHARSET)

    def decrypt(self, enc):
        """
        Funció per desencriptar.
        Rep unicode (el que retorna encrypt) i retorna unicode.
        """
        enc = base64.b64decode(enc)
        iv = enc[:AES.block_size]
        cipher = AES.new(self.key, AES.MODE_CBC, iv)
        decrypted = cipher.decrypt(enc[AES.block_size:])
        return self._unpad(decrypted).decode(APP_CHARSET)
