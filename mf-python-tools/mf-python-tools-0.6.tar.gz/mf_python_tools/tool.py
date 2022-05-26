
import random

def ranstr(num=32, char='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'):
    """随机字符串
        num: 产生的长度，默认：32
    """

    salt = ''
    for i in range(num):
        salt += random.choice(char)

    return salt