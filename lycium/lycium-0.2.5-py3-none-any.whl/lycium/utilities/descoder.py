import Crypto
from Crypto.Cipher import DES
# from Crypto.Util.Padding import pad, unpad

def bchr(s):
    return bytes([s])

def bord(s):
    return s

def pkcs7_pad(data_to_pad, block_size):
    padding_len = block_size-len(data_to_pad)%block_size
    padding = bchr(padding_len)*padding_len
    return data_to_pad + padding

def pkcs7_unpad(padded_data, block_size):
    pdata_len = len(padded_data)
    if pdata_len % block_size:
        # error
        return padded_data
    padding_len = bord(padded_data[-1])
    return padded_data[:-padding_len]

def des_encode(text, dk, encoding='utf-8', encrypt_mode=DES.MODE_ECB):
    cryptor = DES.new(str(dk).encode(encoding), encrypt_mode)
    data = pkcs7_pad(text.encode(encoding), 8)
    ciphertext = cryptor.encrypt(data)
    en_data = ciphertext.hex().upper()
    return en_data

def des_decode(text, dk, encoding='utf-8', encrypt_mode=DES.MODE_ECB):
    cryptor = DES.new(str(dk).encode(encoding), encrypt_mode)
    data = bytes.fromhex(text.lower())
    ciphertext = cryptor.decrypt(data)
    de_data = pkcs7_unpad(ciphertext, 8).decode(encoding)
    return de_data
    