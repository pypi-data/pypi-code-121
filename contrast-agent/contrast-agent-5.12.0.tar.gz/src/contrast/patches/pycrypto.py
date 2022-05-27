# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.


DECRYPT = "decrypt"
PKCS7 = "pkcs7"


def cs__pycrypto_decrypt(original_decrypt, *args, **kwargs):
    """
    :param original_decrypt: decrypt_method
    :param args: 1 => self, 2 => cipher_text
    :return:

    If the mode is CBC attempt to decrypt the cipher_text and validate the padding.
    If the padding is invalid, apply the padding oracle rule.
    """
    value = original_decrypt(*args)

    if not _validate_padding(value, args[0].block_size):
        # the padding oracle rule is (temporarily?) removed from the agent
        # apply_rule("Invalid Padding")
        pass

    return value


def _validate_padding(padded_text, block_size):
    try:
        # import for pycryptodome_patch
        # from Crypto.Util import Padding
        from Cryptodome.Util import Padding

        Padding.unpad(padded_text, block_size, style=PKCS7)
    except ValueError:
        return False
    else:
        return True
