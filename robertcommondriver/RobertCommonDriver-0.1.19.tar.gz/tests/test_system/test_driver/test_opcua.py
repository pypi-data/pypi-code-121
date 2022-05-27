import time
from robertcommondriver.system.driver.opcua import OPCUADriver

#
def call_back(info:str):
    print(info)

def test_scan(dict_config, dict_point):
    dict_point.update(OPCUADriver(dict_config, dict_point).search_points(call_back))
    print(dict_point)

def test_scrap(dict_config, dict_point):

    opcua_driver = OPCUADriver(dict_config, dict_point)

    while True:
        dict_result_scrap = opcua_driver.get_points()
        print(dict_result_scrap)
        time.sleep(5)

def test_case():
    #配置项
    dict_config = {
                        'endpoint': 'opc.tcp://118.24.36.220:62547/DataAccessServer', #'opc.tcp://192.168.1.182:9503/freeopcua/server/',          #url
                        'security': '',                  #
                        'auth': {},          #
                        'subscript_add': 1000,
                        'subscript_interval': 500,
                    }
    #点表
    dict_point = {}

    test_scan(dict_config, dict_point)

    test_scrap(dict_config, dict_point)

    print()

def test_case1():
    #配置项
    dict_config = {
                        'endpoint': 'opc.tcp://42.193.160.84:62541/Quickstarts/ReferenceServer', #'opc.tcp://192.168.1.182:9503/freeopcua/server/',          #url
                        'security': '',                  #
                        'auth': {},          #
                        'subscript_add': 1000,
                        'subscript_interval': 500,
                    }
    #点表
    dict_point = {}

    test_scan(dict_config, dict_point)

    test_scrap(dict_config, dict_point)

    print()

test_case1()