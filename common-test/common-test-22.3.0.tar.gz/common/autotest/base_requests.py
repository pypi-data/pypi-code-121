from common.common.api_driver import APIDriver
from common.plugin.data_plugin import DataPlugin
from common.plugin.data_bus import DataBus
from loguru import logger
from common.autotest.handle_allure import allure_step
from common.autotest.handle_assert import assert_equals
from common.common.constant import Constant
from common.data.data_process import DataProcess
from common.data.handle_common import extractor, get_system_key, set_system_key
from common.file.ReadFile import ReadFile, get_yaml_ApiSchemal
from common.plat.mysql_platform import MysqlPlatForm


class BaseRequest(APIDriver):

    @classmethod
    def send_request(cls, case: list, host: str = 'host', datatype: str='json') -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        if isinstance(case, list):
            if len(case) > 14:
                case_number, case_feature, jira_name, jira_link,case_title, case_severity, path, token, method, parametric_key, file_obj, data, sql, expect, is_save = case
            if len(case) == 14:
                case_number, case_feature, jira_id, case_title, case_severity, path, token, method, parametric_key, file_obj, data, sql, expect, is_save = case
            if len(case) == 13:
                case_feature, jira_id, case_title, case_severity, path, token, method, parametric_key, file_obj, data, sql, expect, is_save = case
        if isinstance(case, dict):
            case_number = DataProcess.get_key_dic(case, Constant.CASE_NO)
            case_title = DataProcess.get_key_dic(case, Constant.CASE_TITLE)
            path = DataProcess.get_key_dic(case, "接口地址")
            status = DataProcess.get_key_dic(case, Constant.CASE_STATUS)
            parametric_key = DataProcess.get_key_dic(case, "入参关键字")
            if DataProcess.get_key_dic(case, Constant.CASE_DATA_TYPE) != None:
                datatype = DataProcess.get_key_dic(case, Constant.CASE_DATA_TYPE)
            token = DataProcess.get_key_dic(case, "token操作")
            method = DataProcess.get_key_dic(case, Constant.CASE_DATA_METHOD)
            file_obj = DataProcess.get_key_dic(case, "上传文件")
            data = DataProcess.get_key_dic(case, Constant.CASE_DATA)
            sql = DataProcess.get_key_dic(case, "后置sql")
            expect = DataProcess.get_key_dic(case, Constant.CASE_EXPECTED)
            is_save = DataProcess.get_key_dic(case, "保存响应")
        logger.info(f"用例进行处理前数据: \n 用例名称: {case_title} \n 接口路径: {path} \n 请求参数: {data} \n 后置sql: {sql} \n 预期结果: {expect} \n 保存响应: {is_save}")
        DataPlugin.excel_convert_allure(case)
        # 处理url、header、data、file、的前置方法
        url = DataProcess.handle_path(path)
        if url.find("http") == -1:
            url = str(get_system_key(host)) + str(DataProcess.handle_path(path))
        cls._convert_url(url)
        logger.info("url:",url)
        allure_step('请求地址', url)
        header = DataProcess.handle_header(token)
        allure_step('请求头', header)
        allure_step('请求类型', method)
        try:
            if datatype == 'json':
                data = DataProcess.handle_data(data)
            else:
                data = DataProcess.handle_data(data, False)
        except:
            data = DataProcess.handle_data(data, False)
        allure_step('请求参数', data)
        file = DataProcess.handler_files(file_obj)
        if file is not None:
            allure_step('上传文件', file_obj)
        # 发送请求
        res = cls.http_request(url, method, parametric_key, header, data, file)
        # 请求后做的事
        allure_step(f'当前响应耗时({res.elapsed.total_seconds()}s)', res.elapsed.total_seconds())
        try:
            if get_system_key(Constant.RUN_TYPE) is not None and get_system_key(Constant.RUN_TYPE).strip() == Constant.RUN_TYPE_JENKINS.strip():
                MysqlPlatForm.insert_api_data(url, method, header, data, res.elapsed.total_seconds(), res.status_code)
                _time, _info =MysqlPlatForm.get_api_data(url, method, header, data, res.elapsed.total_seconds(), res.status_code)
                allure_step(f'历史响应耗时({_time})', _info)
        except:
            logger.warning("保存请求数据异常")
        allure_step(f'响应状态码({res.status_code})', res.status_code)
        allure_step('响应内容', res.text)
        if get_system_key(Constant.RESPONSE_CODE) is not None and res.status_code > int(get_system_key(Constant.RESPONSE_CODE)):
            assert_equals('请求状态码返回错误', f'实际状态码:{res.status_code}', '状态码检查')
        # 响应后操作
        if token == '写':
            DataProcess.have_token['Authorization'] = extractor(res.json(), ReadFile.get_config_value('$.expr.token'))
            allure_step('请求头中添加Token', DataProcess.have_token)
        # 保存用例的实际响应
        if is_save == "yes":
            DataProcess.save_response(case_number, res.json())
        allure_step('存储实际响应', DataProcess.response_dict)
        try:
            return res.json(), expect, res
        except:
            return res.text, expect, res

    @classmethod
    def api_exec(cls, schemal_key, data=None, header=None, file=None, cookie=None, host: str = 'host', datatype: str='json') -> object:
        """处理case数据，转换成可用数据发送请求
        :param case: 读取出来的每一行用例内容，可进行解包
        :param env: 环境名称 默认使用config.yaml server下的 dev 后面的基准地址
        return: 响应结果， 预期结果
        """
        DataBus.save_init_data()
        schemal_data = get_yaml_ApiSchemal(schemal_key)
        url = DataProcess.handle_path(schemal_data['url'])
        if url.find("http") == -1:
            url = get_system_key(host) + DataProcess.handle_path(url)
        cls._convert_url(url)
        allure_step('请求地址', url)
        if data == str:
            data = DataProcess.handle_data(data)
        header = DataProcess.handle_header(header)
        allure_step('请求头', header)
        allure_step('请求类型', schemal_data['method'])
        if datatype == 'json':
            data = DataProcess.handle_data(data)
        else:
            data = DataProcess.handle_data(data, False)
        allure_step('请求参数', data)
        file_obj = DataProcess.handler_files(file)
        if file is not None:
            allure_step('上传文件', file)
        # 发送请求
        res = cls.http_request(url, schemal_data['method'], schemal_data['datatype'], header, data, file_obj, cookie)
        # 请求后做的事
        allure_step(f'当前响应耗时({res.elapsed.total_seconds()}s)', res.elapsed.total_seconds())
        try:
            if get_system_key(Constant.RESPONSE_CODE) is not None and get_system_key(Constant.RUN_TYPE).strip()==Constant.RUN_TYPE_JENKINS.strip():
                MysqlPlatForm.insert_api_data(url, schemal_data['method'], header, data, res.elapsed.total_seconds(), res.status_code)
                _time, _info = MysqlPlatForm.get_api_data(url, schemal_data['method'], header, data, res.elapsed.total_seconds(), res.status_code)
                allure_step(f'历史响应耗时({_time})', _info)
        except:
            logger.warning("保存请求数据异常")
        allure_step(f'响应状态码({res.status_code})', res.status_code)
        allure_step('响应内容', res.text)
        if get_system_key(Constant.RESPONSE_CODE) is not None and res.status_code > int(get_system_key('responseCode')):
            assert_equals('请求状态码返回错误', f'实际状态码:{res.status_code}', '状态码检查')
        return res

    @classmethod
    def _convert_url(self,url):
        _url = url.replace("//", '####').split('/')
        _newurl = '';
        for i in range(len(_url)):
            if _url[i].find(Constant.DATA_NO_CONTENT) == -1:
                _newurl = _newurl + _url[i] + '/'
        _newurl = _newurl.replace("//", "/").replace("####", "//")
        return _newurl



if __name__ == '__main__':
    set_system_key('host',"http://178.83.17.12")
    set_system_key('test2',"AAAA")
    set_system_key('name', "name")
    set_system_key('sex', "sex")
    url="http://127.0.0.1/AAA&在DataBus中未提取到内容!!!&在DataBus中未提取到内容!!!/zhangsan=在DataBus中未提取到内容!!!/lisi/zhangsan在DataBus中未提取到内容!!!/AAA在DataBus中未提取到内容!!!/在DataBus中未提取到内容!!!?id=5/test/333在DataBus中未提取到内容!!!/"
    print(BaseRequest.convert_url(url))









