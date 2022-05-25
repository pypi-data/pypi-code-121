#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re
from io import StringIO

import urllib3


'''
class \r\n
    core.contentExtraction.lineblock\r\n
description\r\n
    行块分析法(内容)\r\n
attribute\r\n
    private __Blocks__\r\n
        type:int\r\n
        default:0\r\n
        description:行块大小\r\n
    private __ChangeRate__\r\n
        type:float\r\n
        default:0.0\r\n
        description:骤变率\r\n
    private __MinLength__\r\n
        type:int\r\n
        default:0\r\n
        description:最小长度\r\n
    private __MapBlock__\r\n
        type:dict()\r\n
        default:{}\r\n
        description:行块列表\r\n
'''
class lineblock:
    __Blocks__=0
    __ChangeRate__=0.0
    __MinLength__=0 
    __MapBlock__=dict()

    def __init__(self,bl_size,cr,mlength):
        '''
        Feature\r\n
            __init__(self,bl_size,cr,mlength)\r\n
        Description\r\n
            初始化\r\n
        Args\r\n
            bl_size\r\n
                type:int\r\n
                description:块偏移\r\n
            cr\r\n
                type:float\r\n
                description:骤变率\r\n
            mlength\r\n
                type:int\r\n
                description:行最小长度\r\n
        '''
        self.__Blocks__=bl_size
        self.__ChangeRate__=cr
        self.__MinLength__=mlength
    
    def createBlocks(self,content):
        '''
        Feature\r\n
            createBlocks(self,content)\r\n
        Description\r\n
            建立块\r\n
        Args\r\n
            content\r\n
                type:string\r\n
                description:内容\r\n
        '''
        ctext=self.filter_tags(content)
        f=StringIO(ctext)
        try:
            #过滤不必要HTML内容生成纯文本
            blockline='' #行块内容 
            blockcount=0   #行块号
            thecount=0     #计数器
            re_line=re.compile(r'[\r\n]',re.I | re.M) #过滤换行
            while True:
                line=f.readline()
                if line=='':
                    break
                line=re_line.sub('',line) #过滤换行
                if len(line)<=self.__MinLength__ and len(blockline)/2-len(line)<=self.__MinLength__:
                    #TODO
                    if thecount<self.__Blocks__:
                        blockline=blockline+line
                        thecount=thecount+1
                    else:
                        if blockline:
                            self.__MapBlock__[blockcount]=blockline
                            blockcount=blockcount+1
                        thecount=0
                        blockline=line
                else:
                    #TODO
                    if blockline:
                        self.__MapBlock__[blockcount]=blockline
                        blockcount=blockcount+1
                    thecount=0
                    blockline=line
                print(line)
                print("-----------------------")
            #处理文本末尾字符
            if thecount!=0:
                self.__MapBlock__[blockcount+1]=blockline
            return True
        except:
            return False
        finally:
            f.flush()
            f.close()

    def getBody(self,ctext):
        '''
        Feature\r\n
            getBody(self,ctext)\r\n
        Description\r\n
            获取内容\r\n
        Args\r\n
            ctext\r\n
                type:string\r\n
                description:需要分析的内容\r\n
        '''
        if self.createBlocks(ctext):
            try:
                currentBlock=len(self.__MapBlock__[0])
                lastBlock=0
                contentBlock={}
                #计算骤变率
                for currentItem in self.__MapBlock__:
                    lastBlock=currentBlock
                    currentBlock=len(self.__MapBlock__[currentItem])
                    between=abs(currentBlock-lastBlock)/max(currentBlock,lastBlock)
                    if currentBlock>self.__MinLength__:
                        contentBlock[currentItem]=between
                    else:
                        if between >= self.__ChangeRate__:
                            contentBlock[currentItem]=between
                #获取正文
                if contentBlock:
                    resultItem=None
                    maxLen=0
                    for Item in contentBlock:
                        if len(self.__MapBlock__[Item])>maxLen:
                            maxLen=len(self.__MapBlock__[Item])
                            resultItem=Item
                    if resultItem:
                        if maxLen>=self.__MinLength__*1.5:
                            return self.__MapBlock__[resultItem]
                        else:
                            return ""
                    else:
                        return ""
                else:
                    return ""
            except:
                pass
            finally:
                pass
        else:
           pass

    def filter_tags(self,htmlstr):
        '''
        Feature\r\n
            filter_tags(self,htmlstr)\r\n
        Description\r\n
            过滤标签\r\n
        Args\r\n
            htmlstr:\r\n
                type:string\r\n
                description:HTML源码\r\n
        '''
        #先过滤CDATA
        re_cdata=re.compile('//<!\[CDATA\[[^>]*//\]\]>',re.I) #匹配CDATA
        re_script=re.compile(r'<script.*?>[\s\S]*?</script*.?>', re.I | re.M)#Script
        re_style=re.compile('<\s*style[^>]*>[^<]*<\s*/\s*style\s*>',re.I)#style
        re_br=re.compile('<br\s*?/?>')#处理换行
        re_comment=re.compile('<!--[^>]*?-->',re.I | re.M)#HTML注释
        re_bian=re.compile(r'<!--[\s\S]+?-->', re.I | re.M)#去除编译条件
        re_h=re.compile('</?\w+[^>]*?>')#HTML标签
        re_stopwords=re.compile('\u3000')#去除无用的'\u3000'字符
        re_tabs=re.compile(r'[\f|\t|\v]',re.I | re.M)#去除制表符等；
        re_tags=re.compile(r'<(\S*?)[^>]*>.*?|<.*? />',re.I | re.M) #过滤剩余的TAGS
        blank_line=re.compile(r'[\r\n]+',re.I | re.M)
        re_space=re.compile(r' ')#去除空格
        s=re_script.sub('',htmlstr)
        s=re_style.sub('',s)#去掉style
        s=re_cdata.sub('',s)#去掉CDATA
        s=re_br.sub('',s)#将br转换空
        s=re_comment.sub('',s)#去掉HTML注释
        s=re_bian.sub('',s)#去除编译条件
        s=re_h.sub('',s) #去掉HTML 标签
        s=re_space.sub('',s)#去掉空格
        s=re_stopwords.sub('',s)#去掉多余的空行
        s=re_tabs.sub('',s)#去掉多余制表符等
        s=blank_line.sub('\n',s)
        s=self.replaceCharEntity(s)#替换实体
        s=re_tags.sub('',s) #过滤剩余TAGS
        return s

    ##替换常用HTML字符实体.
    #使用正常的字符替换HTML中特殊的字符实体.
    #你可以添加新的实体字符到CHAR_ENTITIES中,处理更多HTML字符实体.
    #@param htmlstr HTML字符串.
    def replaceCharEntity(self,htmlstr):
        '''
        Feature\r\n
            replaceCharEntity(self,htmlstr)\r\n
        Description\r\n
            替换HTML字符(特殊字符)\r\n
        Args\r\n
            htmlstr\r\n
                type:string\r\n
                description:要过滤的字符\r\n
        '''
        CHAR_ENTITIES={'nbsp':' ','160':' ',
                    'lt':'<','60':'<',
                    'gt':'>','62':'>',
                    'amp':'&','38':'&',
                    'quot':'"','34':'"',}

        re_charEntity=re.compile(r'&#?(?P<name>\w+);')
        sz=re_charEntity.search(htmlstr)
        while sz:
            entity=sz.group()#entity全称，如&gt;
            key=sz.group('name')#去除&;后entity,如&gt;为gt
            try:
                htmlstr=re_charEntity.sub(CHAR_ENTITIES[key],htmlstr,1)
                sz=re_charEntity.search(htmlstr)
            except KeyError:
                #以空串代替
                htmlstr=re_charEntity.sub('',htmlstr,1)
                sz=re_charEntity.search(htmlstr)
        return htmlstr
    def getPageType(self,args,domain):
        re_href=re.compile('href=\".*?\"',re.I)
        re_link=re.compile('<link.*.?>',re.I)
        args=re_link.sub("",args)
        return "list",""