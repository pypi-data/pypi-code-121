from Crypto.Cipher import AES
import base64


def aes_encrypt(key, content) -> str:
    """
    aes加密
    @param key: 固定的16位秘钥
    @param content: 明文信息
    @return: 密文信息
    """
    aes = AES.new(str.encode(key), AES.MODE_ECB)
    encode_pwd = str.encode(content.rjust(16, '@'))
    encrypt_str = str(base64.encodebytes(aes.encrypt(encode_pwd)), encoding='utf-8')
    return encrypt_str


def aes_decrypt(key, content) -> str:
    """
    aes解密
    @param key: 加密时传入的16位秘钥
    @param content: 密文信息
    @return: 明文信息
    """
    aes = AES.new(str.encode(key), AES.MODE_ECB)
    decrypt_str = (aes.decrypt(base64.decodebytes(content.encode(encoding='utf-8'))).decode().replace('@', ''))
    return decrypt_str


