"""
使用allure需要下载，并配置到环境变量，下载地址：https://github.com/allure-framework/allure2/releases
"""
import json
import os
import allure
import pytest
import inspect as sys_inspect


# 报告模块
def feature(text):
    return allure.feature(text)


# 报告子模块
def story(text):
    return allure.story(text)


# 报告子模块，兼容历史版本
def module(text):
    return allure.story(text)


# 报告标题
def title(text):
    return allure.title(text)


# 报告步骤
def step(text):
    return allure.step(text)


def order(index):
    """
    指定用例执行顺序
    doc: https://blog.csdn.net/weixin_43880991/article/details/116221362
    """
    return pytest.mark.run(order=index)


def depend(*args, **kwargs):
    """
    设置用例依赖关系
    doc: https://www.cnblogs.com/se7enjean/p/13513131.html
    """
    return pytest.mark.depenency(*args, **kwargs)


# 参数化数据
def data(*args, **kwargs):
    """
    @data('key1,key2', [[value1, value2], [value3, value4]])
    """
    return pytest.mark.parametrize(*args, **kwargs)


# 从json文件获取数据进行参数化
def file_data(data_key=None, file_name=None):
    """
    @file_data('key1,key2', 'data.json')
    data.json
        {
            "key1,key2": [[value1, value2], [value3, value4]]
        }
    """
    # 获取被装饰方法的目录
    stack_t = sys_inspect.stack()
    ins = sys_inspect.getframeinfo(stack_t[1][0])
    file_dir = os.path.dirname(os.path.abspath(ins.filename))
    parent_dir = os.path.dirname(file_dir)
    parent_dir_dir = os.path.dirname(parent_dir)
    parent_dir_dir_dir = os.path.dirname(parent_dir_dir)

    # 判断当前、父目录、爷目录、太爷爷目录下的test_data目录下是否有file_name文件
    path_list = [file_dir, parent_dir, parent_dir_dir, parent_dir_dir_dir]
    file_path = None
    full_list = []
    for _path in path_list:
        full_path = os.path.join(_path, 'test_data', file_name)
        full_list.append(full_path)
        # print(full_path)
        if os.path.isfile(full_path) is True:
            file_path = full_path
            break
    if file_path is None:
        raise Exception(f"can not found {file_name} in {full_list}")

    # 根据文件路径以及key获取文件中的数据，暂时只支持json文件
    with open(file_path, 'r', encoding='utf-8') as f:
        json_data = json.load(f)

    content = json_data[data_key]
    return data(data_key, content)
