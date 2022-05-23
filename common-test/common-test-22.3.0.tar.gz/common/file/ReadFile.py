import os
import yaml
import xlrd
from common.config.config import CONFIG_PATH, API_YAML_PATH, CONFIG_YAML_PATH
from common.data.handle_common import extractor, req_expr
from common.file.handle_system import adjust_path_data


class ReadFile:

    @classmethod
    def read_config(cls, file_name, config_path: str = CONFIG_PATH) -> dict:
        """读取配置文件，并且转换成字典
        :param config_path: 配置文件地址， 默认使用当前项目目录下的config/config.yaml
        return cls.config_dict
        """
        if file_name and config_path:
            # 指定编码格式解决，win下跑代码抛出错误
            with open(os.path.join(config_path, file_name), 'r', encoding='utf-8') as f:
                cls.config_dict = yaml.load(f.read(), Loader=yaml.SafeLoader)
                return cls.config_dict


    @classmethod
    def get_config_value(cls, file_name, expr: str = '.') -> dict:
        """默认读取config目录下的config.yaml配置文件，根据传递的expr jsonpath表达式可任意返回任何配置项
        :param expr: 提取表达式, 使用jsonpath语法,默认值提取整个读取的对象
        return 根据表达式返回的值

        调用时传两个参数，一个为yaml文件名，一个为yaml文件中取的值
        """
        return extractor(cls.read_config(file_name), expr)

    @classmethod
    def get_yaml_config(cls,  expr: str = '.',error_flag: bool=True) -> dict:
        """默认读取config目录下的config.yaml配置文件，根据传递的expr jsonpath表达式可任意返回任何配置项
        :param expr: 提取表达式, 使用jsonpath语法,默认值提取整个读取的对象
        return 根据表达式返回的值

        调用时传两个参数，一个为yaml文件名，一个为yaml文件中取的值
        """
        return extractor(cls.read_config(CONFIG_YAML_PATH), expr,error_flag)

    @classmethod
    def get_yaml_ApiSchemal(cls, expr: str = '.') -> dict:
        """默认读取config目录下的config.yaml配置文件，根据传递的expr jsonpath表达式可任意返回任何配置项
        :param expr: 提取表达式, 使用jsonpath语法,默认值提取整个读取的对象
        return 根据表达式返回的值

        调用时传两个参数，一个为yaml文件名，一个为yaml文件中取的值
        """
        return cls.get_config_value(API_YAML_PATH, expr)


    @classmethod
    def get_testcase(cls,testData_path, sheet_name: str=''):
        """
        读取excel格式的测试用例
        :return: data_list - pytest参数化可用的数据
        """
        testData_path=adjust_path_data(testData_path)
        data_list = []
        book = xlrd.open_workbook(testData_path)
        # 读取第一个sheet页
        if sheet_name is None or sheet_name=='':
            table = book.sheet_by_index(0)
        else:
            table=book.sheet_by_name(sheet_name)
        for row in range(1, table.nrows):
            # 每行第5列 是否运行
            if table.cell_value(row, 8) != '否':  # 每行第5列等于否将不读取内容
                value = table.row_values(row)
                value.pop(5)
                data_list.append(list(value))
        return data_list

    @classmethod
    def get_all_data(cls, testData_path, sheet_name: str = ''):
        """
        读取excel格式的测试用例
        :return: data_list - pytest参数化可用的数据
        """
        testData_path = adjust_path_data(testData_path)
        data_list = []
        book = xlrd.open_workbook(testData_path)
        # 读取第一个sheet页
        if sheet_name is None or sheet_name == '':
            table = book.sheet_by_index(0)
        else:
            table = book.sheet_by_name(sheet_name)
        for row in range(0, table.nrows):
            # 每行第5列 是否运行
            value = table.row_values(row)
            value.pop(5)
            data_list.append(list(value))
        return data_list


def get_yaml_config(content, is_dict: bool = True):
    if is_dict:
        return eval(req_expr(str(ReadFile.get_yaml_config(content))))
    else:
        return req_expr(str(ReadFile.get_yaml_config(content, False)))


def get_yaml_ApiSchemal(content, is_dict: bool = True):
    if is_dict:
        return eval(req_expr(str(ReadFile.get_yaml_ApiSchemal(content))))
    else:
        return req_expr(str(ReadFile.get_yaml_config(content, False)))


if __name__ == '__main__':
    # print(ReadFile.get_testcase())
    # print(ReadFile.read_config('ApiSchemal.yaml'))
    # print(ReadFile.get_config_value('config.yaml', 'test'))
    # url = ReadFile.get_config_value('ApiSchemal.yaml', 'server')
    # print(get_yaml_config('test'))
    os.environ['test333']='33343'
    print(get_yaml_ApiSchemal('login')['url'])
    # os.environ['env'] = 'test'








