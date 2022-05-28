'''
模块介绍
    ● 本模块是对 AES-CBC-256 加密算法的二次封装。
    ● 本模块基于 pycryptodome 。
    ● 加密时，程序会自动设置随机iv和随机salt，并生成原始明文的校验值。
    ● 解密时，程序会自动校验"解密得到的明文与初始明文是否一致"。
    ● 本模块可用于加密 字符串、字节串、文件。

功能列表
    ● 加密字节串
    ● 解密字节串
    ● 加密字节串，并写入到硬盘
    ● 从硬盘读取密文，并解密
'''

import hashlib
from random import choices
from pathlib import Path as libpath
from Crypto.Cipher.AES import new as AesNew  # pip install pycryptodome
from Crypto.Cipher.AES import MODE_CBC
from .toolkit.data_structures import SetAttrError


_ObjSet = object.__setattr__
def random_bytes(size): return bytes(choices(range(256), k=size))
# 不使用 os.urandom(size) , 因为它性能较低.

class KeyType(Exception): ...
class SaltSize(Exception): ...
class CheckSize(Exception): ...
class KeyContent(Exception): ...


class cbc256():

    def __init__(self, password):
        # 密钥可以是 bytes、str、int 类型，程序将自动转化为bytes型
        # 密钥允许使用空字符和空字节
        _ObjSet(self, 'password', self.__key_into_bytes(password))

    def __setattr__(self, key, value): raise SetAttrError('cbc256是不可变对象')  # 为了保证password的稳定性
    
    def __key_into_bytes(self, key):
        if type(key) is bytes: return key
        if type(key) is str: return key.encode('utf8')
        if type(key) is int: return str(key).encode('utf8')
        raise KeyType('密钥类型只能是 bytes、str、int')
    
    def __padding(self, plaintext):
        dsize = 16 - len(plaintext) % 16
        plaintext += chr(dsize).encode('utf8') * dsize
        return plaintext

    def encrypt(self, pltext, salt_size=8, check_size=8):  # type(pltext) is bytes
        if not 1 <= salt_size <= 255: raise SaltSize("盐的长度须介于[1, 255]")  # 超出[0, 255]将导致无法解密, 1<=是我个人要求
        if not 0 <= check_size <= 255: raise CheckSize("校验长度须介于[0, 255]")  # 超出此范围将导致无法解密
        salt = random_bytes(salt_size)
        KeyIvCksalt = hashlib.shake_256(self.password + salt).digest(52)  # hashlib.shake_256支持根据空字节(b'')生成哈希
        cbckey = KeyIvCksalt[:32]
        iv = KeyIvCksalt[32:48]
        check_salt = KeyIvCksalt[48:]
        if check_size:
            check = hashlib.shake_256(check_salt + pltext).digest(check_size)
            # 之所以添加 check_salt, 是为了避免得到的校验值恰好就是另一个加密的密钥
        else:
            check = b''
        PltextPa = self.__padding(pltext)
        RealCipherText = AesNew(key=cbckey, mode=MODE_CBC, iv=iv).encrypt(PltextPa)
        # AES密钥支持128位、192位、256位, 此处 32字节 * 8 = 256位
        # 由于密钥经过 shake_256 转换, 破解难度为: min(256 ** 32, 2 ** 256)
        CipherText = bytes([check_size]) + check + bytes([salt_size]) + salt + RealCipherText
        return CipherText  # type(CipherText) is bytes

    def decrypt(self, citext):  # type(citext) is bytes
        check_size = citext[0]
        check = citext[1: 1 + check_size]
        salt_size = citext[1 + check_size]
        salt = citext[2 + check_size: 2 + check_size + salt_size]
        RealCipherText = citext[2 + check_size + salt_size:]
        KeyIvCksalt = hashlib.shake_256(self.password + salt).digest(52)
        cbckey = KeyIvCksalt[:32]
        iv = KeyIvCksalt[32:48]
        check_salt = KeyIvCksalt[48:]
        PltextPa = AesNew(key=cbckey, mode=MODE_CBC, iv=iv).decrypt(RealCipherText)
        pltext = PltextPa[:-PltextPa[-1]]
        # CBC的__padding区块为16字节(<=127字节), 在此范围内可直接使用ptext[-1]来知道填充了多少
        if check_size:
            if hashlib.shake_256(check_salt + pltext).digest(check_size) != check:
                raise KeyContent('密钥错误')
        return pltext  # type(pltext) is bytes

    def encrypt_to_file(self, path, pltext, salt_size=8, check_size=8):
        CipherText = self.encrypt(pltext, salt_size, check_size)
        libpath(path).write_bytes(CipherText)
    
    def decrypt_from_file(self, path):
        citext = libpath(path).read_bytes()
        return self.decrypt(citext)

if __name__ == '__main__':
    密钥 = '1234'
    明文 = '君不见黄河之水天上来'.encode('utf8')

    cbc = cbc256(密钥)
    密文 = cbc.encrypt(明文)
    明文2 = cbc.decrypt(密文)

    print(密文, 明文2.decode('utf8'), 明文2 == 明文, sep='\n\n')
