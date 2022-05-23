import json
from os import path

from common.data.handle_common import get_system_key
from lxml import etree

from common.common.constant import Constant

from common.plugin.data_plugin import DataPlugin

from common.db.handle_db import MysqlDB

from common.data.data_process import DataProcess
from common.file.ReadFile import ReadFile
from common.plugin.data_bus import DataBus
from common.config.config import TEST_DATA_PATH
from common.file.handle_excel import excel_to_list


class FilePlugin(object):
    @classmethod
    def excel_to_dict(self, file_name, sheet: str='Sheet1', _replace: bool=True, file_path: str=TEST_DATA_PATH,
                      _functionName=None, _suitName=None, _storyId=None, _title=None, _report: bool=False):
        """
           读取Excel中特定sheet的数据，按行将数据存入数组datalist[从第二行开始读数据】
           :param data_file:Excel文件目录
           :param sheet:需要读取的sheet名称
           :return:datalist
           """
        DataBus.save_init_data()
        data_list = excel_to_list(path.join(file_path, file_name,), sheet)
        data_list_new = []
        for case_data in data_list:
            # 如果字典数据中case_name与参数一致
            dict={}
            dict[Constant.CASE_STATUS] = '是'
            if _functionName is not None:
                dict[Constant.CASE_MODEL] = _functionName
            if _storyId is not None:
                dict[Constant.CASE_STORY_NO] = _storyId
            if _suitName is not None:
                dict[Constant.CASE_STORY] = _suitName
            if _title is not None:
                dict[Constant.CASE_TITLE] = _title
            if self._dict_contain(case_data,dict):
                if _report:
                    DataPlugin.excel_convert_allure(case_data)
                if _replace:
                    data_list_new.append(DataBus.get_data(case_data))
                else:
                    data_list_new.append(case_data)

        return data_list_new

    @classmethod
    def excel_to_list(cls, testData_path, sheet_name: str = '', _replace: bool=True, _report: bool=False):
        """
        读取excel格式的测试用例,转换成list
        :return: data_list - pytest参数化可用的数据
        """
        DataBus.save_init_data()
        if _replace:
            _data = DataBus.get_data(ReadFile.get_testcase(testData_path, sheet_name))
        else:
            _data = ReadFile.get_testcase(testData_path, sheet_name)
        if _report:
            DataPlugin.excel_convert_allure(_data)
        return _data

    @classmethod
    def get_all_data(cls, testData_path, sheet_name: str = '', _replace: bool = True):
        """
        获取所以Excel数据并转换为List
        :return: data_list - pytest参数化可用的数据
        """
        DataBus.save_init_data()
        if _replace:
            return DataBus.get_data(ReadFile.get_all_data(testData_path, sheet_name))
        else:
            return ReadFile.get_all_data(testData_path, sheet_name)



    @classmethod
    def load_json(self, file_name, _dict=None, _replace: bool=True, file_path: str=TEST_DATA_PATH, _no_content =0, _remove_null:bool=False):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        DataBus.save_init_data()
        _path = path.join(file_path, file_name,)
        with open(_path, "r") as json_file:
            _json = json.load(json_file)
        if _remove_null:
            if _replace:
                _json = DataBus.get_data(_json, _dict, 2)
            _json = DataPlugin.remove_empty(_json)
        else:
            if _replace:
                _json = DataBus.get_data(_json, _dict, _no_content)
        return _json

    @classmethod
    def load_file(self, file_name, _dict=None, _replace: bool = True, file_path: str = TEST_DATA_PATH, _no_content=0,
                  _remove_null: bool = False,_readMode=1):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :param _readMode (0：一行一行读成list，1：全部一起读出）
        :return:
        """
        DataBus.save_init_data()
        _list=[]
        _path = path.join(file_path, file_name, )
        with open(_path, "r", encoding='utf-8') as _file:
            if _readMode == 0:
                _datas =_file.readlines()
                for _data in _datas:
                    if _remove_null:
                        if _replace:
                            _data = DataBus.get_data(_data, _dict, 2)
                        _data = DataPlugin.remove_empty(_data)
                    else:
                        if _replace:
                            _data = DataBus.get_data(_data, _dict, _no_content)
                    _list.append(_data)
            if _readMode == 1:
                _list = _file.read()
                if _remove_null:
                    if _replace:
                        _list = DataBus.get_data(_list, _dict, 2)
                    _list = DataPlugin.remove_empty(_list)
                else:
                    if _replace:
                        _list = DataBus.get_data(_list, _dict, _no_content)
        return _list

    @classmethod
    def load_xml(self, file_name, _xpath,_dict=None, _replace: bool = True, file_path: str = TEST_DATA_PATH, _no_content=0,
                  _remove_null: bool = False):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        DataBus.save_init_data()
        _path = path.join(file_path, file_name, )
        _tree = etree.parse(_path)
        for bbox in _tree.xpath(_xpath):  # 获取bndbox元素的内容
            for corner in bbox.getchildren():  # 便利bndbox元素下的子元素
                _xml = corner.text  # string类型
        if _remove_null:
            if _replace:
                _data = DataBus.get_data(_xml, _dict, 2)
            _data = DataPlugin.remove_empty(_xml)
        else:
            if _replace:
                _data = DataBus.get_data(_xml, _dict, _no_content)
        return _data

    @classmethod
    def load_more_json(self, file_name, _dict=None, _remove_null:bool=False, file_path: str=TEST_DATA_PATH,):
        """
        把Json模版转换为JSON数据,默认找不到数据用空代替
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        DataBus.save_init_data()
        _path = path.join(file_path, file_name,)





    @classmethod
    def mysql_load_list_dict(self, _sql=None, _config=None):
        """
        把数据库中的表作为dict
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        if _config is None:
            _config = {"host": "10.92.80.147", "db_name": "traffic_test", "port": 3306, "user": "mysql",
                     "password": "test1234"}
        _mysql=MysqlDB(_config)
        _list =_mysql.execute(_sql).fetchall()
        _mysql.close()
        return _list

    @classmethod
    def mysql_load_dict(self, _sql=None, _config=None):
        """
        把数据库中的表作为dict
        :param file_name:
        :param replace:
        :param _dict:
        :param file_path:
        :return:
        """
        if _config is None:
            _config = {"host": "10.92.80.147", "db_name": "traffic_test", "port": 3306, "user": "mysql",
                     "password": "test1234"}
        _mysql = MysqlDB(_config)
        _list = _mysql.execute(_sql).fetchone()
        _mysql.close()
        return _list

    @classmethod
    def _dict_contain(self,_data,_temp):
        _flag = True
        self._get_jenkin_TestCaseMark(_data)
        for i, j in _data.items():
            if i in _temp.keys():
                if j != str(DataProcess.get_key_dic(_temp, i)).strip():
                    _flag = False
        return _flag

    @classmethod
    def _get_jenkin_TestCaseMark(self,_dict):
        if get_system_key('TestCaseMark') is not None and get_system_key('TestCaseMark').strip() !='':
            _mark=get_system_key('TestCaseMark')
            if _mark.find(";")!=-1:
                _arr=_mark.split(';')
                for _temp in _arr:
                    _tempKey=_temp.split('&')
                    _dict[_tempKey[0]]=_dict[1]
            else:
                _dict[Constant.CASE_PRIORITY]=get_system_key('TestCaseMark')
        return _dict





if __name__ == '__main__':
    _data='{"orderInfoDetail":{"orderNo":"235423"}}'
    _dict= FilePlugin.load_json("calculateFee.json",_replace=True, _no_content=4)
    print(_dict)




