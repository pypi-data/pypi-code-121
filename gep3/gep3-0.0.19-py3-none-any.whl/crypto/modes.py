"""modes.py: Block cipher modes of operation
"""

# Standard library imports

# Third party imports

# Local application imports
import common.hstr as _hstr

def ecb_encryption(enc, key, block):
    """ecb_encryption()
    """
    ciphertext = ''
    for i in range(len(block)//16):
        plaintext = block[i*16:(i+1)*16]
        ciphertext += enc(key, plaintext)

    return ciphertext

def ecb_decryption(dec, key, block):
    """ecb_decryption()
    """
    plaintext = ''
    for i in range(len(block)//16):
        ciphertext = block[i*16:(i+1)*16]
        plaintext += dec(key, ciphertext)

    return plaintext

def cbc_encryption(enc, key, block, iv):
    """cbc_encryption()
    """
    tmp = iv
    ciphertext = ''
    for i in range(len(block)//16):
        plaintext = block[i*16:(i+1)*16]
        tmp = enc(key, _hstr.xor(tmp, plaintext))
        ciphertext += tmp

    return ciphertext


def cbc_decryption(dec, key, block, iv):
    """cbc_decryption()
    """
    tmp = iv
    plaintext = ''
    for i in range(len(block)//16):
        ciphertext = block[i*16:(i+1)*16]
        plaintext += _hstr.xor(tmp, dec(key, ciphertext))
        tmp = ciphertext

    return plaintext
