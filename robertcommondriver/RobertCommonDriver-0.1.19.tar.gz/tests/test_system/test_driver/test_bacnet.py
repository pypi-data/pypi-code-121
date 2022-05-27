
from robertcommondriver.system.driver.bacnet import BacnetDriver

#回调函数
def call_back(content:str):
    print(content)

#测试扫点
def test_scan(dict_config, dict_point):
    nCount = 1
    while nCount > 0:
        dict_point.update(BacnetDriver(dict_config, dict_point).search_points({'debug_log': call_back}))
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
                        'address': '192.168.42.36/24:47808',          # bacnet server ip(绑定网卡)
                        'identifier': 555,                  # bacnet server identifier
                        'name': 'BacnetDriver',          # bacnet server name
                        'max_apdu': 1024,                   # bacnet server max apdu
                        'segmentation': 'segmentedBoth',     # bacnet server segmentation
                        'vendor_identifier': 15,            # bacnet server vendor
                        'multi_read': 20,                             # bacnet 批量读取个数
                        'cmd_interval': 0.3,                         # bacnet命令间隔
                        'time_out': 5                               # 超时时间
                    }
    #点表
    dict_point = {'6_4_1_analogValue_1': {'point_name': '6_4_1_analogValue_1', 'index': 2, 'point_writable': 'True', 'point_device_address': '6:2/604/192.168.1.184', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '1', 'point_description': '', 'objectName': 'Random-604-1', 'presentValue': '1.0'},
'6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True', 'point_device_address': '192.168.1.208','point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': '3', 'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'},
#'6_4_3_analogValue_3': {'point_name': '6_4_3_analogValue_3', 'index': 4, 'point_writable': 'True', 'point_device_address': '6:4/604','point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '3', 'point_description': '', 'objectName': 'Random-604-3', 'presentValue': '3.0'},
#'6_4_4_analogValue_4': {'point_name': '6_4_4_analogValue_4', 'index': 5, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '4', 'point_description': '', 'objectName': 'Random-604-4', 'presentValue': '4.0'},
#'6_4_5_analogValue_5':  {'point_name': '6_4_5_analogValue_5', 'index': 6, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '5', 'point_description': '', 'objectName': 'Random-604-5', 'presentValue': '5.0'},
#'6_4_6_analogValue_6': {'point_name': '6_4_6_analogValue_6', 'index': 7, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '6', 'point_description': '', 'objectName': 'Random-604-6', 'presentValue': '6.0'},
#'6_4_7_analogValue_7': {'point_name': '6_4_7_analogValue_7', 'index': 8, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '7', 'point_description': '', 'objectName': 'Random-604-7', 'presentValue': '7.0'},
#'6_4_8_analogValue_8': {'point_name': '6_4_8_analogValue_8', 'index': 9, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '8', 'point_description': '', 'objectName': 'Random-604-8', 'presentValue': '8.0'},
#'6_4_9_analogValue_9' : {'point_name': '6_4_9_analogValue_9', 'index': 10, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '9', 'point_description': '', 'objectName': 'Random-604-9', 'presentValue': '9.0'},
#'6_4_10_analogValue_10':  {'point_name': '6_4_10_analogValue_10', 'index': 11, 'point_writable': 'True', 'point_device_address': '6:4/604', 'point_type': 'analogValue', 'point_property': 'presentValue', 'point_address': '10', 'point_description': '', 'objectName': 'Random-604-10', 'presentValue': '10.0'}
                  }


    dict_point1 = {
        '192_168_1_184_3_analogInput_3':
    {'point_name': '192_168_1_184_3_analogInput_3', 'index': 5, 'point_writable': 'True',
     'point_device_address': '192.168.1.184/150',  'point_type': 'analogInput',
     'point_property': 'presentValue', 'point_address': '3', 'point_description': 'bacnet03', 'objectName': 'bacnet03',
     'presentValue': '11.0'},
    '192_168_1_184_4_analogInput_4':
    {'point_name': '192_168_1_184_4_analogInput_4', 'index': 6, 'point_writable': 'True',
     'point_device_address': '192.168.1.184/150', 'point_type': 'analogInput',
     'point_property': 'presentValue', 'point_address': '4', 'point_description': 'bacnet04', 'objectName': 'bacnet04',
     'presentValue': '60.0'},
    '192_168_1_184_5_analogInput_5':
    {'point_name': '192_168_1_184_5_analogInput_5', 'index': 7, 'point_writable': 'True',
     'point_device_address': '192.168.1.184/150', 'point_type': 'analogInput',
     'point_property': 'presentValue', 'point_address': '5', 'point_description': 'bacnet05', 'objectName': 'bacnet05',
     'presentValue': '34.0'},
    '192_168_1_184_6_analogInput_6':
    {'point_name': '192_168_1_184_6_analogInput_6', 'index': 8, 'point_writable': 'True',
     'point_device_address': '192.168.1.184/150',  'point_type': 'analogInput',
     'point_property': 'presentValue', 'point_address': '6', 'point_description': 'bacnet06', 'objectName': 'bacnet06',
     'presentValue': '40.0'},
    '192_168_1_184_7_analogInput_7':
    {'point_name': '192_168_1_184_7_analogInput_7', 'index': 9, 'point_writable': 'True',
     'point_device_address': '192.168.1.184/150', 'point_type': 'analogInput',
     'point_property': 'presentValue', 'point_address': '7', 'point_description': 'bacnet07', 'objectName': 'bacnet07',
     'presentValue': '97.0'}


    }
    #test_scan(dict_config, dict_point)

    test_scrap(dict_config, dict_point)

    print()

test_case()
