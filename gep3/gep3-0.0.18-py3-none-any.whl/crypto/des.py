"""des.py
"""

# Standard library imports
import math as _math

# Third party imports

# Local application imports
import common.hstr as _hstr
import common.bitstr as _bitstr
import common.str as _str

import crypto.modes as modes

_IP = [58, 50, 42, 34, 26, 18, 10, 2, 60, 52, 44, 36, 28, 20, 12, 4, 62, 54, 46, 38, 30, 22, 14, 6, 64, 56, 48, 40, 32, 24, 16,
       8, 57, 49, 41, 33, 25, 17, 9, 1, 59, 51, 43, 35, 27, 19, 11, 3, 61, 53, 45, 37, 29, 21, 13, 5, 63, 55, 47, 39, 31, 23, 15, 7]
_IPINV = [40, 8, 48, 16, 56, 24, 64, 32, 39, 7, 47, 15, 55, 23, 63, 31, 38, 6, 46, 14, 54, 22, 62, 30, 37, 5, 45, 13, 53, 21, 61,
          29, 36, 4, 44, 12, 52, 20, 60, 28, 35, 3, 43, 11, 51, 19, 59, 27, 34, 2, 42, 10, 50, 18, 58, 26, 33, 1, 41, 9, 49, 17, 57, 25]
_PC1 = [57, 49, 41, 33, 25, 17, 9, 1, 58, 50, 42, 34, 26, 18, 10, 2, 59, 51, 43, 35, 27, 19, 11, 3, 60, 52, 44,
        36, 63, 55, 47, 39, 31, 23, 15, 7, 62, 54, 46, 38, 30, 22, 14, 6, 61, 53, 45, 37, 29, 21, 13, 5, 28, 20, 12, 4]
_PC2 = [14, 17, 11, 24, 1, 5, 3, 28, 15, 6, 21, 10, 23, 19, 12, 4, 26, 8, 16, 7, 27, 20, 13, 2,
        41, 52, 31, 37, 47, 55, 30, 40, 51, 45, 33, 48, 44, 49, 39, 56, 34, 53, 46, 42, 50, 36, 29, 32]
_shifts = [1, 1, 2, 2, 2, 2, 2, 2, 1, 2, 2, 2, 2, 2, 2, 1]
_E = [32, 1, 2, 3, 4, 5, 4, 5, 6, 7, 8, 9, 8, 9, 10, 11, 12, 13, 12, 13, 14, 15, 16, 17, 16,
      17, 18, 19, 20, 21, 20, 21, 22, 23, 24, 25, 24, 25, 26, 27, 28, 29, 28, 29, 30, 31, 32, 1]
_P = [16, 7, 20, 21, 29, 12, 28, 17, 1, 15, 23, 26, 5, 18, 31,
      10, 2, 8, 24, 14, 32, 27, 3, 9, 19, 13, 30, 6, 22, 11, 4, 25]
_S = [{'110000': '1111', '110001': '0101', '110101': '0011', '110100': '1001', '010100': '0110', '010101': '1100', '001100': '1011', '001101': '1101', '011110': '0111', '011111': '1000', '001001': '1110', '001000': '0010', '011011': '0101', '011010': '1001', '000110': '0001', '000111': '0100', '000011': '1111', '000010': '0100', '100100': '1110', '100101': '1000', '111100': '0101', '111101': '0110', '100010': '0001', '100011': '1100', '101110': '1011', '101111': '0111', '111001': '1010', '111000': '0011', '101011': '1001', '101010': '0110', '110011': '1011', '110010': '1100', '010010': '1010', '010011': '0110', '010111': '1011', '010110': '1100', '110110': '0111', '110111': '1110', '011000': '0101', '011001': '1001', '001111': '0001', '001110': '1000', '011101': '0011', '011100': '0000', '001010': '1111', '001011': '0010', '101101': '0001', '000000': '1110', '000001': '0000', '100111': '0010', '100110': '1000', '000101': '0111', '000100': '1101', '111111': '1101', '111110': '0000', '100001': '1111', '100000': '0100', '010001': '1010', '010000': '0011', '101100': '0010', '111010': '1010', '111011': '0000', '101000': '1101', '101001': '0100'},
      {'110000': '0101', '110001': '1011', '110101': '0111', '110100': '1100', '010100': '0010', '010101': '0001', '001100': '0011', '001101': '1000', '011110': '1010', '011111': '0101', '001001': '1111', '001000': '0110', '011011': '1001', '011010': '0000', '000110': '1110', '000111': '0111', '000011': '1101', '000010': '0001', '100100': '0111', '100101': '1010', '111100': '0010', '111101': '1110', '100010': '1110', '100011': '1000', '101110': '0001', '101111': '0010', '111001': '0000', '111000': '1001', '101011': '1111', '101010': '0100', '110011': '0110', '110010': '1000',
       '010010': '0111', '010011': '0000', '010111': '1010', '010110': '1101', '110110': '0110', '110111': '1100', '011000': '1100', '011001': '0110', '001111': '1110', '001110': '0100', '011101': '1011', '011100': '0101', '001010': '1011', '001011': '0010', '101101': '0100', '000000': '1111', '000001': '0011', '100111': '0001', '100110': '1011', '000101': '0100', '000100': '1000', '111111': '1001', '111110': '1111', '100001': '1101', '100000': '0000', '010001': '1100', '010000': '1001', '101100': '1101', '111010': '0011', '111011': '0101', '101000': '1010', '101001': '0011'},
      {'110000': '1011', '110001': '0100', '110101': '1110', '110100': '0010', '010100': '1100', '010101': '0101', '001100': '1111', '001101': '0110', '011110': '1000', '011111': '0001', '001001': '0011', '001000': '0110', '011011': '1011', '011010': '0100', '000110': '1110', '000111': '1001', '000011': '0111', '000010': '0000', '100100': '0100', '100101': '1101', '111100': '1110', '111101': '0010', '100010': '0110', '100011': '1010', '101110': '0000', '101111': '0111', '111001': '1011', '111000': '0101', '101011': '1001', '101010': '1111', '110011': '1111', '110010': '0001',
       '010010': '1101', '010011': '1000', '010111': '1110', '010110': '0111', '110110': '1100', '110111': '0011', '011000': '1011', '011001': '1100', '001111': '1010', '001110': '0101', '011101': '1111', '011100': '0010', '001010': '0011', '001011': '0100', '101101': '1000', '000000': '1010', '000001': '1101', '100111': '0000', '100110': '1001', '000101': '0000', '000100': '1001', '111111': '1100', '111110': '0111', '100001': '0001', '100000': '1101', '010001': '0010', '010000': '0001', '101100': '0011', '111010': '1010', '111011': '0101', '101000': '1000', '101001': '0110'},
      {'110000': '1111', '110001': '1001', '110101': '0101', '110100': '0011', '010100': '1000', '010101': '0010', '001100': '1001', '001101': '0000', '011110': '1111', '011111': '1001', '001001': '0110', '001000': '0000', '011011': '1010', '011010': '1100', '000110': '0011', '000111': '0101', '000011': '1000', '000010': '1101', '100100': '1001', '100101': '0000', '111100': '1000', '111101': '0010', '100010': '0110', '100011': '1111', '101110': '1101', '101111': '1000', '111001': '1100', '111000': '0101', '101011': '0001', '101010': '1011', '110011': '0100', '110010': '0001',
       '010010': '0010', '010011': '0111', '010111': '1100', '010110': '0101', '110110': '1110', '110111': '1011', '011000': '1011', '011001': '0001', '001111': '0011', '001110': '1010', '011101': '1110', '011100': '0100', '001010': '0110', '001011': '1111', '101101': '1101', '000000': '0111', '000001': '1101', '100111': '0110', '100110': '0000', '000101': '1011', '000100': '1110', '111111': '1110', '111110': '0100', '100001': '0011', '100000': '1010', '010001': '0100', '010000': '0001', '101100': '0111', '111010': '0010', '111011': '0111', '101000': '1100', '101001': '1010'},
      {'110000': '1111', '110001': '0110', '110101': '0000', '110100': '1100', '010100': '0011', '010101': '1111', '001100': '1011', '001101': '1101', '011110': '1001', '011111': '0110', '001001': '0100', '001000': '0111', '011011': '1001', '011010': '0000', '000110': '0001', '000111': '1100', '000011': '1011', '000010': '1100', '100100': '0001', '100101': '1100', '111100': '0000', '111101': '0101', '100010': '0010', '100011': '1000', '101110': '1000', '101111': '1101', '111001': '1010', '111000': '0110', '101011': '1110', '101010': '1101', '110011': '1111', '110010': '1001',
       '010010': '0101', '010011': '0000', '010111': '1010', '010110': '1111', '110110': '0101', '110111': '1001', '011000': '1101', '011001': '0011', '001111': '0001', '001110': '0110', '011101': '1000', '011100': '1110', '001010': '1010', '001011': '0111', '101101': '0010', '000000': '0010', '000001': '1110', '100111': '0111', '100110': '1011', '000101': '0010', '000100': '0100', '111111': '0011', '111110': '1110', '100001': '1011', '100000': '0100', '010001': '0101', '010000': '1000', '101100': '0111', '111010': '0011', '111011': '0100', '101000': '1010', '101001': '0001'},
      {'110000': '0111', '110001': '1011', '110101': '0001', '110100': '0100', '010100': '0011', '010101': '1101', '001100': '0110', '001101': '1001', '011110': '1011', '011111': '1000', '001001': '0111', '001000': '1001', '011011': '1011', '011010': '0111', '000110': '1111', '000111': '0010', '000011': '1111', '000010': '0001', '100100': '1111', '100101': '0010', '111100': '1011', '111101': '1000', '100010': '1110', '100011': '0011', '101110': '0011', '101111': '1010', '111001': '0110', '111000': '0001', '101011': '0101', '101010': '1000', '110011': '1110', '110010': '0000',
       '010010': '1101', '010011': '0001', '010111': '1110', '010110': '0100', '110110': '1010', '110111': '0111', '011000': '1110', '011001': '0000', '001111': '0101', '001110': '1000', '011101': '0011', '011100': '0101', '001010': '0010', '001011': '1100', '101101': '1111', '000000': '1100', '000001': '1010', '100111': '1100', '100110': '0101', '000101': '0100', '000100': '1010', '111111': '1101', '111110': '0110', '100001': '0100', '100000': '1001', '010001': '0110', '010000': '0000', '101100': '1100', '111010': '1101', '111011': '0000', '101000': '0010', '101001': '1001'},
      {'110000': '1010', '110001': '1001', '110101': '0000', '110100': '0110', '010100': '1001', '010101': '0101', '001100': '1000', '001101': '0001', '011110': '0001', '011111': '0110', '001001': '0100', '001000': '1111', '011011': '1111', '011010': '1010', '000110': '1110', '000111': '0111', '000011': '0000', '000010': '1011', '100100': '1011', '100101': '1101', '111100': '1001', '111101': '0011', '100010': '0100', '100011': '1011', '101110': '1110', '101111': '0111', '111001': '1110', '111000': '0000', '101011': '0100', '101010': '0011', '110011': '0101', '110010': '1111',
       '010010': '1100', '010011': '0011', '010111': '1100', '010110': '0111', '110110': '1000', '110111': '1111', '011000': '0101', '011001': '0010', '001111': '1010', '001110': '1101', '011101': '1000', '011100': '0110', '001010': '0000', '001011': '1001', '101101': '1010', '000000': '0100', '000001': '1101', '100111': '1000', '100110': '1101', '000101': '1011', '000100': '0010', '111111': '1100', '111110': '0010', '100001': '0110', '100000': '0001', '010001': '1110', '010000': '0011', '101100': '0111', '111010': '0101', '111011': '0010', '101000': '1100', '101001': '0001'},
      {'110000': '0000', '110001': '1111', '110101': '1001', '110100': '1010', '010100': '0011', '010101': '0110', '001100': '1011', '001101': '0111', '011110': '0111', '011111': '0010', '001001': '1010', '001000': '0110', '011011': '1110', '011010': '0000', '000110': '0100', '000111': '1000', '000011': '1111', '000010': '0010', '100100': '0100', '100101': '1110', '111100': '0101', '111101': '0110', '100010': '1011', '100011': '0001', '101110': '0010', '101111': '1101', '111001': '0011', '111000': '1111', '101011': '1010', '101010': '1100', '110011': '1100', '110010': '0110', '010010': '1001', '010011': '0101', '010111': '1011', '010110': '1110', '110110': '1101', '110111': '0000', '011000': '0101', '011001': '0000', '001111': '0100', '001110': '0001', '011101': '1001', '011100': '1100', '001010': '1111', '001011': '0011', '101101': '1000', '000000': '1101', '000001': '0001', '100111': '0111', '100110': '0001', '000101': '1101', '000100': '1000', '111111': '1011', '111110': '1000', '100001': '0010', '100000': '0111', '010001': '1100', '010000': '1010', '101100': '1110', '111010': '0011', '111011': '0101', '101000': '1001', '101001': '0100'}]


def dea_e(key_16h: str, block_16h: str) -> str:
    """dea_e: DES encryption algorithm
    """
    # cleaning inputs
    key_16h = _clean_key(key_16h, 16)
    block_16h = _clean_block(block_16h, 16)

    # converting the input from hexadecimal string to bit string
    block_64 = _hstr.to_bitstr(block_16h)
    key_64 = _hstr.to_bitstr(key_16h)

    # pre-computing the 16 round keys
    roundkeys = _roundkeys(key_64)

    # computing the 16 rounds
    # applying initial permutation
    block_64 = _str.perm(block_64, _IP)
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys[i], L_32, R_32)

    # applying the inversed initial permutation
    block_64 = _str.perm(R_32 + L_32, _IPINV)

    return _bitstr.to_hstr(block_64)


def dea_d(key_16h: str, block_16h: str) -> str:
    """dea_d: DES decryption algorithm
    """
    # cleaning inputs
    key_16h = _clean_key(key_16h, 16)
    block_16h = _clean_block(block_16h, 16)

    # converting the input from hexadecimal string to bit string
    block_64 = _hstr.to_bitstr(block_16h)
    key_64 = _hstr.to_bitstr(key_16h)

    # pre-computing the 16 round keys
    roundkeys = _roundkeys(key_64)
    roundkeys.reverse()

    # computing the 16 rounds
    # applying initial permutation
    block_64 = _str.perm(block_64, _IP)
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys[i], L_32, R_32)

    # applying the inversed initial permutation
    block_64 = _str.perm(R_32 + L_32, _IPINV)

    return _bitstr.to_hstr(block_64)


def dea_ede_cbc(key_16h: str, block_16h_n: str, iv_16h: str) -> str:
    """dea_ede_cbc: Single DES encryption algorithm in CBC mnode
    """
    # cleaning inputs
    key_16h = _clean_key(key_16h, 16)
    block_16h_n = _clean_n_blocks(block_16h_n, 16)
    iv_16h = _clean_block(iv_16h, 16)

    return modes.cbc_encryption(dea_e, key_16h, block_16h_n, iv_16h)


def tdea_2_ede(key_32h: str, block_16h: str) -> str:
    """tdea_2_ede: Triple DES encryption algorithm
    """
    # cleaning inputs
    key_32h = _clean_key(key_32h, 32)
    block_16h = _clean_block(block_16h, 16)

    # DES encryption with key #1

    # converting the input from hexadecimal string to bit string
    block_64 = _hstr.to_bitstr(block_16h)
    key_128 = _hstr.to_bitstr(key_32h)
    key_64 = key_128[0:64]

    # pre-computing the 16 round keys
    roundkeys1 = _roundkeys(key_64)

    # computing the 16 rounds
    # applying initial permutation
    block_64 = _str.perm(block_64, _IP)
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys1[i], L_32, R_32)

    block_64 = R_32 + L_32

    # DES decryption with key #2

    key_64 = key_128[64:128]

    # pre-computing the 16 round keys
    roundkeys2 = _roundkeys(key_64)
    roundkeys2.reverse()

    # computing the 16 rounds
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys2[i], L_32, R_32)

    block_64 = R_32 + L_32

    # DES encryption with key #1

    # computing the 16 rounds
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys1[i], L_32, R_32)

    # applying the inversed initial permutation
    block_64 = _str.perm(R_32 + L_32, _IPINV)

    return _bitstr.to_hstr(block_64)


def tdea_2_ded(key_32h: str, block_16h: str) -> str:
    """tdea_2_ded: Triple DES decryption algorithm
    """
    # cleaning inputs
    key_32h = _clean_key(key_32h, 32)
    block_16h = _clean_block(block_16h, 16)

    # DES decryption with key #1

    # converting the input from hexadecimal string to bit string
    block_64 = _hstr.to_bitstr(block_16h)
    key_128 = _hstr.to_bitstr(key_32h)
    key_64 = key_128[0:64]

    # pre-computing the 16 round keys
    roundkeys1 = _roundkeys(key_64)
    roundkeys1.reverse()

    # computing the 16 rounds
    # applying initial permutation
    block_64 = _str.perm(block_64, _IP)
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys1[i], L_32, R_32)

    block_64 = R_32 + L_32

    # DES encryption with key #2

    key_64 = key_128[64:128]

    # pre-computing the 16 round keys
    roundkeys2 = _roundkeys(key_64)

    # computing the 16 rounds
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys2[i], L_32, R_32)

    block_64 = R_32 + L_32

    # DES decryption with key #1

    # computing the 16 rounds
    # working on block halves of 32 bits
    L_32 = block_64[0:32]
    R_32 = block_64[32:64]

    for i in range(16):
        [L_32, R_32] = _round(roundkeys1[i], L_32, R_32)

    # applying the inversed initial permutation
    block_64 = _str.perm(R_32 + L_32, _IPINV)

    return _bitstr.to_hstr(block_64)


def tdea_2_ede_cbc(key_32h: str, block_16h_n: str, iv_16h: str) -> str:
    """tdea_2_ede_cbc: Triple DES encryption algorithm in CBC mnode
    """
    # cleaning inputs
    key_32h = _clean_key(key_32h, 32)
    block_16h_n = _clean_n_blocks(block_16h_n, 16)
    iv_16h = _clean_block(iv_16h, 16)

    return modes.cbc_encryption(tdea_2_ede, key_32h, block_16h_n, iv_16h)


def tdea_2_ded_cbc(key_32h: str, block_16h_n: str, iv_16h: str) -> str:
    """tdea_2_ded_cbc: Triple DES decryption algorithm in CBC mnode
    """
    # cleaning inputs
    key_32h = _clean_key(key_32h, 32)
    block_16h_n = _clean_n_blocks(block_16h_n, 16)
    iv_16h = _clean_block(iv_16h, 16)

    return modes.cbc_decryption(tdea_2_ded, key_32h, block_16h_n, iv_16h)


def encrypt(key_h: str, block_16h: str) -> str:
    """encrypt(): Single or triple-DES encryption
    """
    key_h = _hstr.clean(key_h, 'encrypt()', 'key_h')
    block_16h = _hstr.clean(block_16h, 'encrypt()', 'block_16h')

    if len(key_h) == 16:
        return dea_e(key_h, block_16h)

    if len(key_h) == 32:
        return tdea_2_ede(key_h, block_16h)

    if len(key_h) == 48:
        return ''


def decrypt(key_h: str, block_16h: str) -> str:
    """decrypt(): Single or triple-DES decryption
    """
    key_h = _hstr.clean(key_h, 'decrypt()', 'key_h')
    block_16h = _hstr.clean(block_16h, 'decrypt()', 'block_16h')

    if len(key_h) == 16:
        return dea_d(key_h, block_16h)

    if len(key_h) == 32:
        return tdea_2_ded(key_h, block_16h)

    if len(key_h) == 48:
        return ''


def kcv(key_h: str) -> str:
    """kcv(): Key Check Value
    """
    return encrypt(key_h, '00' * 8)[0:6]

def mac_1_e(key_h: str, hstr: str):
    """mac_1_e(): single DES MAC generation
    """
    key_h = _hstr.clean(key_h)
    hstr = _hstr.clean(hstr)
    temp = '0' * 16
    for i in range(len(hstr)//16):
        block = hstr[i*16:i*16+16]
        temp = dea_e(key_h, _hstr.xor(temp, block))
    return temp

def mac_2_ede(key_h: str, hstr: str):
    """mac_2_ede(): double DES MAC generation
    """
    key_h = _hstr.clean(key_h)
    hstr = _hstr.clean(hstr)
    key__key_1 = key_h[0:16]
    key__key_2 = key_h[16:32]
    
    mac = mac_1_e(key__key_1, hstr)
    mac = dea_d(key__key_2, mac)
    mac = dea_e(key__key_1, mac)
    
    return mac

#
# DEA inner functions
#


def _roundkeys(rootkey_64):
    roundkeys_16_48 = []

    # applying permutation _PC1
    T_58 = _str.perm(rootkey_64, _PC1)
    # working on key halves of 56 bits
    C_28 = T_58[0:28]
    D_28 = T_58[28:56]

    # computing the 16 roundkeys
    for i in range(16):
        # applying a left circular shift to both key halves
        C_28 = _str.lcs(C_28, _shifts[i])
        D_28 = _str.lcs(D_28, _shifts[i])
        # applying the permutation _PC2
        roundkeys_16_48.append(_str.perm(C_28 + D_28, _PC2))

    return roundkeys_16_48


def _round(roundkey_48, L_32, R_32):
    return [R_32, _bitstr.xor(L_32, _f(roundkey_48, R_32))]


def _f(roundkey_48, block_32):
    # expanding the input block
    block_48 = _str.exp(block_32, _E)

    block_48 = _bitstr.xor(block_48, roundkey_48)

    # substituting the 8 6-bit sub-blocks
    block_32 = ''
    for i in range(8):
        block_32 = block_32 + _S[i][block_48[i*6:i*6+6]]

    # applying the permutation
    block_32 = _str.perm(block_32, _P)

    return block_32

#
# helper functions
#


def _clean_key(key_lh, length):
    key_lh = _hstr.clean(key_lh)
    if len(key_lh) != length:
        raise TypeError(F"Wrong key length: 0x{len(key_lh):X}h")

    return key_lh


def _clean_block(block_lh, length):
    block_lh = _hstr.clean(block_lh)
    if len(block_lh) != length:
        raise TypeError(
            F"Wrong block length: 0x{len(block_lh):X}h instead of 0x{length:02X}")

    return block_lh


def _clean_n_blocks(block_lh_n, length, n=0):
    block_lh_n = _hstr.clean(block_lh_n)
    if n == 0:
        if len(block_lh_n) % length != 0:
            raise TypeError(
                F"Wrong number of blocks: 0x{_math.ceil(len(block_lh_n) / length):X}h")
    else:
        if len(block_lh_n) != length * n:
            raise TypeError(F"Wrong block length: 0x{len(block_lh_n):X}h")

    return block_lh_n
