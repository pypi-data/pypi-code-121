#!/bin/env python
# -*- coding: utf-8-*-
#author: ganruoxun
#date: 2020-09-25

import mmh3
import os
import binascii

class Mmh3Hash(object):
    def __init__(self,_type,resType):
        self.typeDic = {
            "2":"bs",
            "3": "hy",
            "4": "zl",
            "5": "bz",
            "10": "fg",
        }
        self.typeCode = self.typeDic[_type]
        self.resType = resType
        if self.typeCode == None:
            raise RuntimeError('type 参数无法识别！')

    ##从filePath获取文件名，将文件名转大写，后缀转小写
    def normFileName(self,filePath):
        lngid=os.path.splitext(os.path.normpath(os.path.basename(filePath)))[0].upper()
        prfx=os.path.splitext(os.path.normpath(os.path.basename(filePath)))[1].lower()
        return "{0}{1}".format(lngid,prfx)

    ##规范文件名称，文件名转大写，文件后缀转小写
    def normFileName(self,fileName):
        if not "." in fileName:
            return fileName.upper()
        tmps = fileName.split(".")
        filePrfx = tmps[0].upper()
        fileSufx = tmps[1].lower()
        return "{0}{1}".format(filePrfx, fileSufx)

    ## 使用murmurhash3算法将新全文文件名进行HASH并按照规则组装成HASH目录
    def generateHashName(self,fileName):
        hashCode = binascii.b2a_hex(mmh3.hash_bytes(fileName)).upper()[0:3]
        firstCode = chr(hashCode[0])
        secondCode = chr(hashCode[1])
        thirdCode = chr(hashCode[2])
        if thirdCode.isdigit():
            return firstCode + secondCode + str(int(thirdCode)%5)
        elif thirdCode == 'D':
            return firstCode + secondCode + 'A'
        elif thirdCode == 'E':
            return firstCode + secondCode + 'B'
        elif thirdCode == 'F':
            return firstCode + secondCode + 'C'
        else:
            return firstCode + secondCode + thirdCode

    #fileName：文件名称，带后缀，不能为空，专利为公开号加文件后缀名，其他为lngid加文件后缀名
    #years：年份，不能为空
    #country：国家，如果为空，默认为cn
    #type：自建资源类型，不能为空，目前只有bs（博硕）,hy（会议）,bz（标准）,fg（法规）,zl（专利）
    def generatehashPath(self,fileName,years,country,resType):
        if  years == None or len(years) != 4:
            raise RuntimeError('years 参数错误！')
        elif fileName == None or len(fileName) == 0:
            raise RuntimeError('fileName 参数错误！')
        elif country == None or len(country) == 0:
            country = 'cn'
        if resType in ('bs', 'hy', 'fg', 'zl', 'bz'):
            country = "cn"
        country = country.lower()
        intYear = int(years)
        if intYear < 1989:
            years = 'befor1989'
        fileName = normFileName(fileName)
        return "\\" + resType + "\\" + years + country + self.typeCode + "\\" + generateFullPathName(fileName);
        return '\\' + years + country + _type + '\\' + generateHashName(fileName) + '\\' + fileName

