import time
from robertcommondriver.system.driver.modbus import ModbusDriver

#回调函数
def call_back(info:str):
    print(info)

#测试读点
def test_get(dict_config, dict_point):

    modbus_driver = ModbusDriver(dict_config, dict_point)

    #轮询全部
    while True:
        dict_result_scrap = modbus_driver.get_points()
        print(dict_result_scrap)
        time.sleep(2)

#设置
def test_set(dict_config, dict_point):

    modbus_driver = ModbusDriver(dict_config, dict_point)

    dict_result_scrap = modbus_driver.set_points({'modbus_0': 11, 'modbus_2': 22})
    print(dict_result_scrap)

    #轮询全部
    while True:
        dict_result_scrap = modbus_driver.get_points()
        print(dict_result_scrap)
        time.sleep(2)


def test_case():
    #配置项
    dict_config = {
                        'multi_read':'100',                             # 批量读取个数
                        'cmd_interval': '0.3',                         # 命令间隔
                        'time_out': '5'                                 # 超时时间
                    }
    #点表
    dict_point = {}
    dict_point['modbus_0'] = {'point_writable': True, 'point_name': 'modbus_0', 'device_address': '192.168.1.184/502',  'point_slave_id':'1', 'point_fun_code':'3', 'point_address':'0', 'point_data_type':'0', 'point_data_length':'1', 'point_scale':'1'}
    dict_point['modbus_1'] = {'point_writable': True, 'point_name': 'modbus_1', 'device_address': '192.168.1.184/502', 'point_slave_id': '1','point_fun_code': '3', 'point_address': '2', 'point_data_type': '0', 'point_data_length': '1', 'point_scale': '1'}
    dict_point['modbus_2'] = {'point_writable': True, 'point_name': 'modbus_2', 'device_address': '192.168.1.184/502', 'point_slave_id': '1','point_fun_code': '3', 'point_address': '4', 'point_data_type': '0', 'point_data_length': '1', 'point_scale': '1'}

    test_get(dict_config, dict_point)

    print()

test_case()