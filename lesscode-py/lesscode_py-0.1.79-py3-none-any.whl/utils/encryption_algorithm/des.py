import base64

from Crypto.Cipher import DES as Des


class DES:
    @staticmethod
    def encrypt(string: str, key: str, mode=Des.MODE_ECB, encoding='utf-8'):
        pad = 8 - len(string) % 8
        pad_str = "".join([chr(i) for i in range(pad)])
        string += pad_str
        des = Des.new(key=key, mode=mode)
        encrypt_string = base64.b64encode(des.encrypt(string.encode(encoding))).decode(encoding)
        return encrypt_string

    @staticmethod
    def decrypt(string: str, key: str, mode=Des.MODE_ECB, encoding='utf-8'):
        pad = 8 - len(string) % 8
        pad_str = "".join([chr(i) for i in range(pad)])
        string += pad_str
        des = Des.new(key=key, mode=mode)
        decrypt_string = des.decrypt(base64.b64decode(string.encode(encoding))).decode(encoding)
        return decrypt_string
