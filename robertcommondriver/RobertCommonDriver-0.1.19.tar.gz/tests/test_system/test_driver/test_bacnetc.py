import time
from robertcommondriver.system.driver.bacnetc import BacnetDriver


#回调函数
def call_back(info:str):
    print(info)

#测试扫点
def test_scan(dict_config, dict_point):
    nCount = 1
    while nCount > 0:
        dict_point.update(BacnetDriver(dict_config, dict_point).search_points(call_back))
        print(f'scan {len(dict_point)}')
        nCount = nCount - 1

#测试读点
def test_get(dict_config, dict_point):

    bacnet_driver = BacnetDriver(dict_config, dict_point)

    dict_result_get = {}
    for point_name in dict_point.keys():
        dict_result_get.update(bacnet_driver.get_points({point_name:''}))
    print(len(dict_result_get))

def test_scrap(dict_config, dict_point):

    bacnet_driver = BacnetDriver(dict_config, dict_point)

    #轮询全部
    nCount = 20
    while nCount > 0:
        dict_result_scrap = bacnet_driver.get_points()
        print(f'scrap {len(dict_result_scrap)}')
        nCount = nCount - 1

def test_case():
    #配置项
    dict_config = {
                        'address': '192.168.1.42/24:47808',          # bacnet server ip(绑定网卡)
                        'identifier': '555',                  # bacnet server identifier
                        'segmentation': 65,     # bacnet server segmentation
                        'vendor_identifier': '15',            # bacnet server vendor
                        'multi_read':'20',                             # bacnet 批量读取个数
                        'cmd_interval': '0.3',                         # bacnet命令间隔
                        'time_out': '5'                                 # 超时时间
                    }
    #点表
    dict_point = {}

    test_scan(dict_config, dict_point)

    #dict_point = {'192_168_1_184_47808_6_2_602_2_1': {'point_name': '192_168_1_184_47808_6_2_602_2_1', 'index': 0, 'point_writable': 'True', 'device_address': '192.168.1.184:47808:6:2/602', 'point_type': '2', 'point_property': 'presentValue', 'point_address': '1', 'description': 'None', 'present_value': '1.0', 'object_name': 'Random-602-1'}, '192_168_1_184_47808_6_2_602_2_2': {'point_name': '192_168_1_184_47808_6_2_602_2_2', 'index': 0, 'point_writable': 'True', 'device_address': '192.168.1.184:47808:6:2/602', 'point_type': '2', 'point_property': 'presentValue', 'point_address': '2', 'description': 'None', 'present_value': '2.0', 'object_name': 'Random-602-2'}, '192_168_1_184_47808_6_2_602_2_3': {'point_name': '192_168_1_184_47808_6_2_602_2_3', 'index': 0, 'point_writable': 'True', 'device_address': '192.168.1.184:47808:6:2/602', 'point_type': '2', 'point_property': 'presentValue', 'point_address': '3', 'description': 'None', 'present_value': '3.0', 'object_name': 'Random-602-3'}, '192_168_1_184_47808_6_2_602_2_4': {'point_name': '192_168_1_184_47808_6_2_602_2_4', 'index': 0, 'point_writable': 'True', 'device_address': '192.168.1.184:47808:6:2/602', 'point_type': '2', 'point_property': 'presentValue', 'point_address': '4', 'description': 'None', 'present_value': '4.0', 'object_name': 'Random-602-4'}, '192_168_1_184_47808_6_2_602_2_5': {'point_name': '192_168_1_184_47808_6_2_602_2_5', 'index': 0, 'point_writable': 'True', 'device_address': '192.168.1.184:47808:6:2/602', 'point_type': '2', 'point_property': 'presentValue', 'point_address': '5', 'description': 'None', 'present_value': '5.0', 'object_name': 'Random-602-5'}, '192_168_1_184_47808_6_2_602_2_6': {'point_name': '192_168_1_184_47808_6_2_602_2_6', 'index': 0, 'point_writable': 'True', 'device_address': '192.168.1.184:47808:6:2/602', 'point_type': '2', 'point_property': 'presentValue', 'point_address': '6', 'description': 'None', 'present_value': '6.0', 'object_name': 'Random-602-6'}}

    test_scrap(dict_config, dict_point)

    print()

test_case()