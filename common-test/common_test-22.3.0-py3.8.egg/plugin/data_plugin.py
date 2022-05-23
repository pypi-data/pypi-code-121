import json
from typing import Iterable

from common.common.constant import Constant

from common.autotest.handle_allure import allure_title, allure_severity, allure_feature, allure_link, allure_story, \
    allure_suite

from common.data.data_process import DataProcess

from common.data.handle_common import req_expr, convert_json, extractor
from common.plat.jira_platform import JiraPlatForm


class DataPlugin(object):
    @classmethod
    def convert_json(self, _temp, _replace: bool = True):
        """
        任意的数据类型转换成Json
        :param _temp:
        :param _replace: 是否清洗数据
        :return:
        """
        content = _temp
        if isinstance(_temp, str):
            content = json.loads(content)
        else:
            content = json.dumps(_temp)
        if _replace:
            content = req_expr(content)
        return content

    @classmethod
    def json_convert_dict(self, _json, _replace: bool = True) -> dict:
        """
              Json字符串转换为字典
              :param _json:
              :param _replace: 是否清洗数据
              :return:
              """
        if _replace:
            _json = req_expr(_json)
        return convert_json(_json)

    @classmethod
    def get_key_dic(self,_data, key):
        return DataProcess.get_key_dic(_data,key)


    @classmethod
    def get_data_jpath(self, obj: dict, expr: str = '.', error_flag: bool = False):
        """
            通过Jpath获取json数据
        :param obj:
        :param expr:
        :param error_flag:
        :return:
        """
        return extractor(obj, expr, error_flag)

    @classmethod
    def load_json_object(self,_json):
        newObj = dict()
        DataProcess.parseJson(_json, newObj)
        return self.del_dict_no_content(newObj)


    @classmethod
    def _json_empty(self, _item):
        if isinstance(_item, Iterable):
            return not _item
        elif isinstance(_item, str):
            return _item == ''
        else:
            return False


    @classmethod
    def remove_empty(self,item):
        if isinstance(item, dict):
            new_item = {k: self.remove_empty(v) for k, v in item.items()}
            return {k: v for k, v in new_item.items() if not self._json_empty(v)}
        elif isinstance(item, (list, tuple)):
            new_item = [self.remove_empty(v) for v in item]
            return [v for v in new_item if not self._json_empty(v)]
        else:
            return item

    @classmethod
    def get_date(self, now):
       return DataProcess.getDate(now)




    @classmethod
    def excel_convert_allure(self, data):
        if isinstance(data, dict):
            _title = DataProcess.get_key_dic(data,Constant.CASE_TITLE)
            _severity = DataProcess.get_key_dic(data,Constant.CASE_PRIORITY)
            _feature = DataProcess.get_key_dic(data,Constant.CASE_MODEL)
            _StoryName = DataProcess.get_key_dic(data,Constant.CASE_STORY)
            _suitName = DataProcess.get_key_dic(data,Constant.CASE_STORY)
            _StoryLink = ""
            if DataProcess.get_key_dic(data, Constant.CASE_STORY_NO) is not None and str(
                    DataProcess.get_key_dic(data, Constant.CASE_STORY_NO)).strip() != '':
                _StoryName, _StoryLink,jira_no = JiraPlatForm.getJiraIssueSummer(DataProcess.get_key_dic(data, Constant.CASE_STORY_NO))
            if DataProcess.get_key_dic(data,Constant.CASE_LINK) is not None and str(
                    DataProcess.get_key_dic(data, Constant.CASE_LINK)).strip() != '':
                _StoryName, _StoryLink, jira_no = JiraPlatForm.getJiraIssueSummer(DataProcess.get_key_dic(data,Constant.CASE_LINK))
            if _StoryName is None:
                _StoryName = str(DataProcess.get_key_dic(data, Constant.CASE_STORY)).strip()
                _StoryLink = str(DataProcess.get_key_dic(data, Constant.CASE_LINK)).strip()
        if isinstance(data, list):
            _feature = data[1]
            _suitName = data [2]
            _StoryName, _StoryLink, jira_no = JiraPlatForm.getJiraIssueSummer(
                data[2].strip())
            if _StoryName is not None:
                _title = data[3]
                _severity = data[4]
            else:
                _StoryName, _StoryLink, jira_no = JiraPlatForm.getJiraIssueSummer(
                    data[3].strip())
                if _StoryName is not None:
                    _title = data[4]
                    _severity = data[5]
                else:
                    _StoryName = data[2]
                    _StoryLink = data[3]
                    _title = data[4]
                    _severity = data[5]
        allure_title(_title)
        # allure报告 用例模块
        allure_feature(_feature)
        allure_severity(_severity)
        allure_story(_StoryName)
        # 测试套件
        if _suitName is not None and str(_suitName).strip() !='':
            allure_suite(_suitName)




if __name__ == '__main__':
    str1 = '{"listData": "333","strData": "test python obj 2 json"}'
    print(DataPlugin.convert_json(str1))





