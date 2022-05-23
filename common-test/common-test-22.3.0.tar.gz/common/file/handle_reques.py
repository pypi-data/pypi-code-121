import json
from jsonpath import jsonpath
import re
from common.config.config import TEST_DATA_PATH
from common.file.handle_system import adjust_path


def get_request_params(paramsPath):
    """
    读取json文件中的接口请求参数，读取出来的内容是字符串格式
    :param paramsPath: 文件的路径，不包含项目路径
    :return: dict格式的请求数据
    """
    with open(adjust_path(TEST_DATA_PATH + paramsPath),'r',encoding='utf8')as fp:
        params_json = fp.read()
        return params_json

def get_re_params(content,expr:str='"&(.*?)&"'):
    """
    替换为可以进行jsonpath方式提取的json字符串
    :param content:json格式的字符串
    :param expr:正则表达式
    :return:
    """
    for i in re.findall(expr,content):
        content =content.replace(f'&{i}&',i)
    # print(content)
    return content

def handle_data_by_jsonPath(requestData,scenesParams):
    """
    用场景参数替换请求参数中的某些参数
    :param requestData: 请求参数
    :param scenesParams: 场景参数
    :return:替换后的请求参数
    """
    requestData = json.loads(requestData)
    for k,v in requestData.items():
        if type(v) not in [int,bool]:
            if '$.' in v:
                requestData[k] =jsonpath(scenesParams,v)[0]
    # print(requestData)
    return requestData


if __name__ == '__main__':
    params_json = get_request_params(r'\queryFlightFareList.Json')
    content = get_re_params(params_json)
    # sheet_data= get_excel_data(testData_path+'\\integrated_case.xls',0)
    # handle_data_by_jsonPath(content,sheet_data[0][5])
