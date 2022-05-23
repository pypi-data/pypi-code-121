import ast
import json
import os
import time
from os import path
from loguru import logger
from common.autotest.handle_allure import allure_step
from common.config.config import TEST_FILE_PATH, TEST_DATA_PATH
from common.data.handle_common import req_expr, convert_json
from common.file.ReadFile import get_yaml_config


class DataProcess:
    response_dict = {}
    @classmethod
    def save_response(cls, key: str, value: object) -> None:
        """
        保存实际响应
        :param key: 保存字典中的key，一般使用用例编号
        :param value: 保存字典中的value，使用json响应
        """
        cls.response_dict[key] = value
        logger.info(f'添加key: {key}, 对应value: {value}')


    @classmethod
    def handle_path(cls, path_str: str) -> str:
        """路径参数处理
        :param path_str: 带提取表达式的字符串 /&$.case_005.data.id&/state/&$.case_005.data.create_time&
        上述内容表示，从响应字典中提取到case_005字典里data字典里id的值，假设是500，后面&$.case_005.data.create_time& 类似，最终提取结果
        return  /511/state/1605711095
        """
        # /&$.case.data.id&/state/&$.case_005.data.create_time&
        return req_expr(path_str, cls.response_dict)

    @classmethod
    def handle_header(cls, token) -> dict:
        """处理header
        :param token: 写： 写入token到header中， 读： 使用带token的header， 空：使用不带token的header
        return
        """
        if token == 'None':
            return None
        if token == '空':
            return ''
        if token is None or str(token) == '':
            header = get_yaml_config('$.common.request_headers')
        else:
            if isinstance(token, str) and token.find('$.common') != -1:
                header = get_yaml_config(token)
            else:
                header = token
        if token == '读':
            header = cls.handle_data_fromat(header.copy())
        else:
            header = cls.handle_data_fromat(header)
        if isinstance(header, dict):
            return header
        else:
            return ast.literal_eval(header)

    @classmethod
    def handler_files(cls, file_obj: str) -> object:
        """file对象处理方法
        :param file_obj: 上传文件使用，格式：接口中文件参数的名称:"文件路径地址"/["文件地址1", "文件地址2"]
        实例- 单个文件: &file&D:
        """
        d = path.dirname(__file__)
        # 返回当前d文件的父目录地址
        parent_path = os.path.dirname(d)

        if file_obj == '' or file_obj is None:
            return
        for k, v in convert_json(file_obj).items():
            # 多文件上传
            if isinstance(v, list):
                files = []
                for ex_path in v:
                    all_path = os.sep.join([TEST_FILE_PATH,ex_path])
                    files.append((k, (open(all_path, 'rb'))))
                    # print(all_path)

            else:
                # 单文件上传
                all_path = os.sep.join([TEST_FILE_PATH, v])
                files = {k: open(all_path, 'rb')}
            return files

    @classmethod
    def handle_data_fromat(cls, _template, data=None, _no_content=0, _dataType:bool=False):
        if isinstance(_template, str):
            if isinstance(data, list):
                _dict = []
                for _index in range(len(data)):
                    if isinstance(data[_index], dict):
                        _dict.append(cls.handle_data_fromat(_template, data[_index]))
                return _dict
            else:
                return req_expr(content= _template, data= data, _no_content = _no_content, _dataType = _dataType)
        else:
            if isinstance(_template, list):
                for _index in range(len(_template)):
                    _template[_index] = cls.handle_data_fromat(_template[_index], data, _no_content, _dataType)
                return _template
            else:
                if isinstance(_template, dict):
                    for key in _template.keys():
                        _template[key] = cls.handle_data_fromat(_template[key], data, _no_content, _dataType)
                return _template

    @classmethod
    def handle_data(cls, variable: str, jsonformat:bool=True) -> dict:
        """请求数据处理
        :param variable: 请求数据，传入的是可转换字典/json的字符串,其中可以包含变量表达式
        return 处理之后的json/dict类型的字典数据
        """
        if variable == '':
            return
        if isinstance(variable, str) and variable.find(".json",len(variable)-5) != -1:
            _path = path.join(TEST_DATA_PATH, variable, )
            with open(_path, "r") as json_file:
                variable = json.load(json_file)
        data = req_expr(variable, cls.response_dict)
        if jsonformat:
            variable = convert_json(data)
        else:
            variable = data
        return variable

    @classmethod
    def handle_sql(cls, sql: str, db: object):
        """处理sql，并将结果写到响应字典中"""
        if sql :
            sql = req_expr(sql, cls.response_dict)
            allure_step('运行sql', sql)
            logger.info(sql)
            # 查后置sql
            result = db.fetch_one(sql)
            allure_step('sql执行结果', {"sql_result": result})
            logger.info(f'结果：{result}')
            if result:
                # 将查询结果添加到响应字典里面，作用在，接口响应的内容某个字段 直接和数据库某个字段比对，在预期结果中
                # 使用同样的语法提取即可
                cls.response_dict.update(result)
        else:
            sql = None
            return

    @classmethod
    def get_key_dic(self, _data, _key):
        _temp=None
        if isinstance(_data,dict):
            _temp = _data.get(_key.strip())
            if _temp is None:
                for c in _data.keys():
                    if str(c).strip().lower() == _key.strip().lower():
                        _temp = _data.get(c)
            if _temp is None:
                for c in _data.keys():
                    if str(c).strip().lower().find(_key.strip().lower()) != -1:
                        _temp = _data.get(c)
            return _temp
        if isinstance(_data,list):
            for c in range(len(_data)):
                if str(_data[c]).strip()== _key.strip():
                    _temp = c
            if _temp is None:
                for c in range(len(_data)):
                    if str(_data[c]).strip().lower() == _key.strip().lower():
                        _temp = c
            if _temp is None:
                for c in range(len(_data)):
                    if str(_data[c]).strip().lower().find(_key.strip().lower()) != -1:
                        _temp = c
            return _temp

    @classmethod
    def parseJson(self, obj, newObj):
        '''
        递归遍历json
        '''
        for k in obj:
            # 为list的时候
            if isinstance(obj, list):
                if isinstance(k, list):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(k, list()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(k, list())
                elif isinstance(k, dict):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(k, dict()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(k, dict())
                else:
                    # 这一段 判断key
                    if isinstance(newObj, list):
                        newObj.append(k)
                    elif isinstance(newObj, dict):
                        newObj[k] = k
            # 为dict的时候
            elif isinstance(obj, dict):
                if isinstance(obj[k], list):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(obj[k], list()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(obj[k], list())
                elif isinstance(obj[k], dict):
                    if isinstance(newObj, list):
                        newObj.append(self.parseJson(obj[k], dict()))
                    elif isinstance(newObj, dict):
                        newObj[k] = self.parseJson(obj[k], dict())
                else:
                    # 这一段 判断key
                    if isinstance(newObj, list):
                        newObj.append(obj[k])
                    elif isinstance(newObj, dict):
                        newObj[k] = obj[k]
        return newObj

    @classmethod
    def getDate(self,now):
        if isinstance(now,str):
            now=int(now)
        timeArray = time.localtime(now)
        _time = time.strftime("%Y-%m-%d %H:%M:%S", timeArray)
        return _time

    @classmethod
    def getDateDiff(self,_date):
        _date = str(_date).strip()
        if len(_date) > 10:
            ts = int(time.mktime(time.strptime(_date, "%Y-%m-%d %H:%M:%S")))
        else:
            ts = int(time.mktime(time.strptime(_date, "%Y-%m-%d")))
        return ts


if __name__ == '__main__':
    # _list=['aaaa','ccc',"AA","bbbccc"]
    # print(DataProcess.get_key_dic(_list,'bbb'))


    #print(get_yaml_config('$.common.request_headers'))

     # file_obj = '{"files":["data/pic002.jpeg"]}'
     # print(da.handler_files(file_obj))
    # print(get_yaml_config('$.common.request_headers'))
    # str='4883838/38384'
    # if str.find(".json", len(str) - 5) != -1:
    #     print("11")
    # else:
    #     print("222")
    obj = {
        "a": 1,
        "b": {
            "c": 2,
            "d": 3,
            "e": 4,
            "f": [5, 6, {"g": 7, "h": 8}]
        }
    }

    newObj = dict()
    DataProcess.parseJson(obj, newObj)
    del newObj['a']
    print(f"newObj --> {newObj}")




