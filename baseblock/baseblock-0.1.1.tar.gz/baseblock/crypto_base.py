#!/usr/bin/env python
# -*- coding: UTF-8 -*-
""" Crytography Base Functions """


import os

from cryptography.fernet import Fernet

enc = "utf-8"


class CryptoBase(object):
    """ Crytography Base Functions """

    def __init__(self):
        """
        Created:
            2-Mar-2022
            craig@grafflr.ai
            *   https://github.com/grafflr/graffl-core/issues/209
        """
        self._key = "vYuJ9Y4_FtIlClfTsvIiMTDg4x-Xco_FeGWxNpo_7Sw=" # os.environ['POETRY_FERNET_KEY']

    def encrypt_str(self,
                    some_input: str) -> str:
        return self.encrypt(some_input.encode(enc))

    def encrypt(self,
                message: bytes) -> str:
        f = Fernet(self._key)
        return str(f.encrypt(message))

    def decrypt_str(self,
                    some_input: str) -> str:
        return self.decrypt(some_input.encode(enc))

    def decrypt(self,
                message: bytes) -> str:
        f = Fernet(self._key)
        return f.decrypt(message).decode(enc)


def main(param1, param2):
    def _action():
        if param1 == "encrypt":
            return CryptoBase().encrypt_str(param2)
        elif param1 == "decrypt":
            return CryptoBase().decrypt_str(param2)
        else:
            raise NotImplementedError("\n".join([
                "Unknown Param: {}".format(param1)]))

    print(_action())


if __name__ == "__main__":
    import plac

    plac.call(main)
