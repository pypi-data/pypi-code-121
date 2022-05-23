import yaml
from common.data.handle_common import extractor

from common.config.config import CONFIG_PATH
from common.file.handle_system import adjust_path

def get_yaml_data(filePath):
    """
    获取yaml文件信息返回JSON数据
    :param filePath: 文件名称
    :return: JOSN数据
    """
    with open(adjust_path(filePath),encoding='UTF-8') as f:
        fData = f.read()  # 读出来yaml文件数据
        yamlData = yaml.safe_load(fData)  # 将文件数据通过yaml形式加载
        return yamlData

def get_yaml_dict(filePath,key:str):
    """
    获取yaml文件信息返回JSON数据
    :param filePath: 文件名称
    :return: JOSN数据
    """
    with open(adjust_path(filePath),encoding='UTF-8') as f:
        fData = f.read()  # 读出来yaml文件数据
        yamlData = yaml.safe_load(fData)  # 将文件数据通过yaml形式加载
    if key is not None:
        yamlData = extractor(yamlData,key)
        return yamlData
    else:
        return yamlData




if __name__ == '__main__':
    print(get_yaml_data(CONFIG_PATH+'/config.yaml'))
    print(get_yaml_dict(CONFIG_PATH + '/config.yaml',"test.ibs_test"))