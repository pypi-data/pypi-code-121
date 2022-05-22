import hashlib 
import uuid
from random import randint
from typing import Union


def stringMd5(string: str) -> str:
    '''
    计算字符串MD5值
    '''
    return hashlib.md5(string.encode()).hexdigest()


def generateServiceKey() -> str:
    '''
    生成一个服务密钥
    '''
    # 生成两个服务UUID
    serviceUUID1 = uuid.uuid1().hex
    serviceUUID2 = uuid.uuid1().hex
    serviceUUID2Length = len(serviceUUID2)

    # 随机截取第二个UUID2中的部分字符串用做MD5的盐值
    startIndex = randint(0, serviceUUID2Length / 2)
    endIndex = randint(serviceUUID2Length / 2, serviceUUID2Length)

    return stringMd5(f'{serviceUUID1}{serviceUUID2[startIndex:endIndex]}')