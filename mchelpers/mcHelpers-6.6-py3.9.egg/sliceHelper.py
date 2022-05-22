# -*- coding: utf-8 -*-
'''
@Time    : 2022/5/22 9:54 PM
@Author  : oujiewen2@shoplineapp.com
@File    : sliceHelper.py
'''
import sys
sys.path.append("..")

class sliceHelper:
    def __init__(self):
        pass

    def intToBin(self,number, index, feature=True):
        """index为该数据位宽,number为待转换数据,
        feature为True则进行十进制转二进制，为False则进行二进制转十进制。"""

        if (feature == True):  # 十进制转换为二进制
            if (number >= 0):
                b = bin(number)
                b = '0' * (index + 2 - len(b)) + b
            else:
                b = 2 ** (index) + number
                b = bin(b)
                b = '1' * (index + 2 - len(b)) + b  # 注意这里算出来的结果是补码
            b = b.replace("0b", '')
            b = b.replace('-', '')
            return b
        elif (feature == False):  # 二进制转换为十进制
            i = int(str(number), 2)
            if (i >= 2 ** (index - 1)):  # 如果是负数
                i = -(2 ** index - i)
                return i
            else:
                return i

    def tableId(self,storeId, maxId):
        a = self.intToBin(storeId, 64)
        b = '0' * 32 + a[0:32]
        c = ''
        for i in range(len(a)):
            if a[i] == b[i]:
                c += '1'
            else:
                c += '0'
        return ((int('0b' + c[32:], base=2))+1) % int(maxId)

if __name__ == '__main__':
    sliceHelper=sliceHelper()
    print(sliceHelper.tableId(1639980798319,64))


