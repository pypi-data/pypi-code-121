from pyDes import des, CBC, PAD_PKCS5
import hashlib
import os
import binascii
import time
 
# 秘钥
def des_encrypt(s,secret_key):
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    return binascii.b2a_hex(en)
 
 
def des_descrypt(s,secret_key):
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de

def getfilemd5(filepath):
    if not os.path.isfile(filepath):
        raise Exception("Get MD5 error,it is not a file")
    f = open(filepath,'rb')
    filehash = hashlib.md5()
    
    while True:
        bs = f.read(8096)
        if not bs:
            break
        filehash.update(bs)
    f.close()
    return filehash.hexdigest()

if __name__ == '__main__':
    md5 = getfilemd5('c:\\360base.dll')

    
    print(e-s)