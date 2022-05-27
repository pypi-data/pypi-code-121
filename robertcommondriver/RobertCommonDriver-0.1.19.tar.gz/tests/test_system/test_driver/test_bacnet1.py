from robertcommondriver.system.driver.bacnet import BacnetDriver

#回调函数
def call_back(content:str):
    print(content)

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
'6_4_2_analogValue_2': {'point_name': '6_4_2_analogValue_2', 'index': 3, 'point_writable': 'True', 'point_device_address': '192.168.1.208','point_type': 'analogInput', 'point_property': 'presentValue', 'point_address': '3', 'point_description': '', 'objectName': 'Random-604-2', 'presentValue': '2.0'}}

    test_scrap(dict_config, dict_point)

    print()

test_case()