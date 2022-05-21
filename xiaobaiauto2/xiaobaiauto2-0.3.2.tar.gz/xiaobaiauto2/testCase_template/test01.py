#! /usr/bin/env python
__author__ = 'Tser'
__email__ = '807447312@qq.com'
__project__ = 'xiaobaiauto2'
__script__ = 'test01.py'
__create_time__ = '2020/7/17 2:15'

import pytest

def setup_module():
    print("整个文档执行前执行一次")

def teardown_module():
    print("整个文件执行后执行一次")

def setup_function():
    print("执行每个方法前执行一次，不适合单接口")

def teardown_function():
    print("执行每个方法后执行一次，不适合单接口")


def test_xiaobai_api():
    print("执行接口测试")
    assert '实际返回值' != '预期值'

class TestClass(object):

    def setup_class(self):
        print("setup_class(self)：每个类之前执行一次")

    def teardown_class(self):
        print("teardown_class(self)：每个类之后执行一次")

    def test_xiaobai_api2(self):
        print("执行接口测试")
        assert '实际返回值' != '预期值'

# if __name__=="__main__":
#     pytest.main(["-s", "test_xiaobai_api.py"])
# 或者命令行运行生成HTML报告，命令如下
# pytest --html=report.html --self-contained-html