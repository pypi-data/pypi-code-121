#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'utils.py'
__create_time__ = '2020/11/2 19:15'

from typing import Optional
from yaml import load_all, dump_all
import pysnooper


@pysnooper.snoop()
class ModelBase(object):
    def __init__(self, file: Optional[str] = '', mode: Optional[str] = 'r', encoding: Optional[str] = 'utf-8'):
        '''
            初始化
        :param file:        文件名
        :param model:       模式
        :param encoding:    编码
        '''
        self.obj = open(file=file, mode=mode, encoding=encoding)

    def convert(self, lod: Optional[str], new: Optional[str], encoding: Optional[str] = 'utf-8'):
        '''
            格式转换
        :param lod: json|yaml|yam|xml
        :param new: json|yaml|yam|xml
        :param encoding: utf-8
        :return:
        example:
            convert(old='json', new='yaml')
            or
            convert(old='json', new='yam', encoding='gbk')
        '''

    def json2yaml(self):
        ''' json file convert to yaml file '''
        pass

    def yaml2json(self):
        ''' yaml file convert to json file '''

    def xml2json(self):
        ''' xml file convert to json file '''

    def cmdRun(self):
        ''' pytest run '''
        pass

    def yamlRun(self):
        ''' yaml file run '''
        pass

    def jsonRun(self):
        ''' json file run '''
        pass

class ApiHandle(ModelBase):
    def json2yaml(self):
        pass