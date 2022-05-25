import base64

from Crypto.PublicKey import RSA as Rsa
from Crypto.Cipher import PKCS1_v1_5 as Cipher_pkcs1_v1_5
from Crypto import Random


class RSA:
    @staticmethod
    def generate_key():
        _random_generator = Random.new().read
        # rsa算法生成实例
        _rsa = Rsa.generate(1024, _random_generator)
        # 私钥的生成
        _private_key = _rsa.exportKey()
        # 公钥的生成
        _public_key = _rsa.publickey().exportKey()
        key = {
            "private_key": _private_key,
            "public_key": _public_key
        }
        return key

    @staticmethod
    def encrypt(string: str, public_key: str, encoding='utf-8'):
        rsa_key = Rsa.importKey(public_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        encrypt_string = base64.b64encode(cipher.encrypt(string.encode(encoding))).decode(encoding)
        return encrypt_string

    @staticmethod
    def decrypt(string: str, private_key: str, encoding='utf-8'):
        rsa_key = Rsa.importKey(private_key)
        cipher = Cipher_pkcs1_v1_5.new(rsa_key)
        decrypt_string = cipher.decrypt(base64.b64decode(string.encode(encoding)), "解密失败").decode(encoding)
        return decrypt_string
