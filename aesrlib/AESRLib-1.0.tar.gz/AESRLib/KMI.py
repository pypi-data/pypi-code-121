import os
import base64
import binascii
import random
from Crypto import Random
from Crypto.Cipher import AES
from Crypto.Protocol.KDF import PBKDF2

class kmi:
    def __init__(self):
        self.plength=32
        self.carray = [chr(i) for i in range(32, 126)]

    def stob(self, s: str) -> bytes:
        return binascii.unhexlify(s)

    def btos(self, b: bytes) -> str:
        return str(binascii.hexlify(b))[2:-1]

    def getprivatekey(self, passwd: str) -> tuple[bytes, bytes]:
        salt = os.urandom(16)
        key = PBKDF2(passwd, salt, 64, 1000)
        return (key[:32],salt)

    def returnpkey(self, pwd: str, salt: bytes) -> bytes:
        key = PBKDF2(pwd, salt, 64, 1000)
        return key[:32]

    def createconf(self, pwd: str):
        ppass = self.getprivatekey(pwd)
        iv=Random.new().read(AES.block_size)
        return (AES.new(ppass[0], AES.MODE_CBC, iv), ppass[1], iv)

    def getconf(self, inpass: str, pKey: str):
        if(inpass is not None and pKey is not None):
            pwd=self.returnpkey(inpass, self.stob(pKey[:self.plength]))
            iv=self.stob(pKey[self.plength:2*self.plength])
            return AES.new(pwd, AES.MODE_CBC, iv)
        else:
            raise ValueError("You can't proceed without entering pKey/password!")

    def createalpha(self) -> list[str]:
        alpha=[chr(i) for i in random.sample(range(32, 126), 94)]
        return alpha

    def alphamap(self, rarray: list[str]) -> dict[str,str]:
        cmap=dict(zip(self.carray,rarray))
        return cmap

    def transalphamap(self, rlist: list[str], loc: int) -> dict[str,str]:
        rgen=base64.b64decode(rlist.pop(loc).encode('utf-8')).decode('utf-8')
        transalpha=dict(zip(list(rgen),self.carray))
        return transalpha