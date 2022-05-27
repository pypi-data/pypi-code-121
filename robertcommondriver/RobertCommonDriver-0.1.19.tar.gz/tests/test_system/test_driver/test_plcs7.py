import time
from robertcommondriver.system.driver.plcs7 import SiemensS7Driver


def test_all():
    dict_config = {'multi_read': 20, 'cmd_interval': 0.3, 'send_timeout': 15, 'rec_timeout': 3500}
    dict_point = {}
    dict_point['plc1'] = {'point_writable':True, 'point_name':'plc1','device_address':'192.168.1.111','rack':'0','slot':'1','address':'DB3,REAL4','scale':'1'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'plc2', 'device_address': '192.168.1.111', 'rack': '0', 'slot': '1', 'address': 'DB3,REAL8', 'scale': '1'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'plc3', 'device_address': '192.168.1.111', 'rack': '0','slot': '1', 'address': 'DB2,INT2', 'scale': '1'}
    dict_point['plc4'] = {'point_writable': True, 'point_name': 'plc4', 'device_address': '192.168.1.111', 'rack': '0','slot': '1', 'address': 'DB1,BOOL0.0', 'scale': '1'}
    driver = SiemensS7Driver(dict_config, dict_point)
    dit_reslut = driver.set_points({'plc2': 123.456, 'plc3':'12', 'plc4': 0})

    while True:
        point_dict = driver.get_points()
        print(point_dict)
        time.sleep(5)


def test_case():
    test_all()

test_case()