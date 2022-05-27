import time
from robertcommondriver.system.driver.obix import ObixDriver

#回调函数
def call_back(info:str):
    print(info)

#测试扫点
def test_scan():
    point_dict = ObixDriver({'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'timeout':30},{}).search_points(call_back)
    print(point_dict)

#测试读点
def test_get():
    point_dict = {}
    point_dict['test1'] = {'point_name': 'test1', 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_2/points/CHW_ENT','point_type': 'real', 'point_writable': False,  'point_description':''}
    point_dict['test2'] = {'point_name': 'test2', 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_2/points/CHW_SPT','point_type': 'real', 'point_writable': False,  'point_description':''}
    driver = ObixDriver({'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081'},point_dict)
    if driver.ping_target() == True:
        result = driver.get_points(point_dict)  # 读取点
        print(result)

#测试轮询点
def test_scrap():
    point_dict = {
        'Chiller_1_CHW_ENT': {'point_name': 'Chiller_1_CHW_ENT', 'point_writable': True, 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CHW_ENT/', 'point_type': 'real', 'point_description': '43.50 °F {ok}', 'val': '43.5'},
        'Chiller_1_CHW_LVT': {'point_name': 'Chiller_1_CHW_LVT', 'point_writable': True, 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CHW_LVT/', 'point_type': 'real', 'point_description': '44.20 °F {ok}', 'val': '44.20000076293945'},
        'Chiller_1_CW_ENT': {'point_name': 'Chiller_1_CW_ENT', 'point_writable': True, 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CW_ENT/', 'point_type': 'real', 'point_description': '79.50 °F {ok}', 'val': '79.5'},
        'Chiller_1_CW_LVT': {'point_name': 'Chiller_1_CW_LVT', 'point_writable': True, 'point_url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CW_LVT/', 'point_type': 'real', 'point_description': '79.70 °F {ok}', 'val': '79.69999694824219'},
        }

    driver = ObixDriver({'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'timeout':10},point_dict)
    while True:
        point_dict = driver.get_points()
        print(point_dict)
        time.sleep(5)

# 测试轮询点
def test_scrap1():
    point_dict = {
        'Chiller_1_CHW_ENT': {'name': 'Chiller_1_CHW_ENT', 'point_writable': True,
                              'url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CHW_ENT/', 'type': 'real',
                              'description': '43.50 °F {ok}', 'val': '43.5'},
        'Chiller_1_CHW_LVT': {'name': 'Chiller_1_CHW_LVT', 'point_writable': True,
                              'url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CHW_LVT/', 'type': 'real',
                              'description': '44.20 °F {ok}', 'val': '44.20000076293945'},
        'Chiller_1_CW_ENT': {'name': 'Chiller_1_CW_ENT', 'point_writable': True,
                             'url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CW_ENT/', 'type': 'real',
                             'description': '79.50 °F {ok}', 'val': '79.5'},
        'Chiller_1_CW_LVT': {'name': 'Chiller_1_CW_LVT', 'point_writable': True,
                             'url': '/obix/config/Drivers/BacnetNetwork/Chiller_1/points/CW_LVT/', 'type': 'real',
                             'description': '79.70 °F {ok}', 'val': '79.69999694824219'},
    }

    driver = ObixDriver(
        {'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://localhost:5002', 'timeout': 10},
        point_dict)
    while True:
        point_dict = driver.get_points()
        print(point_dict)
        time.sleep(5)
    driver._del_watch()

def test_scan1():
    #point_dict = ObixDriver({'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://localhost:5002', 'timeout':30},{}).search_points(call_back)
    point_dict = ObixDriver(
        {'username': 'beop_sample', 'password': 'RNB.beop-2020', 'url': 'http://localhost:5002', 'timeout': 30},
        {}).search_points(call_back)
    print(point_dict)


def test_all():
    #dict_config = {'username': 'beop_sample', 'password': 'RNB.beop-2020', 'url': 'http://localhost:5002', 'timeout': 30}
    dict_config = {'username': 'beop_798', 'password': 'RNB.beop-2020', 'url': 'https://driversimulator.ari-smart.com', 'timeout': 30}
    dict_point = {}
    dict_point = ObixDriver(dict_config, dict_point).search_points(call_back)
    print(dict_point)

    driver = ObixDriver(dict_config, dict_point)
    while True:
        point_dict = driver.get_points()
        print(point_dict)
        time.sleep(5)
    driver._del_watch()

def test_all1():
    dict_config = {'username': 'beop_798', 'password': 'RNB.beop-2020', 'url': 'http://localhost:5002', 'url1': 'http://52.168.76.233:5001', 'timeout': 30}
    #dict_config = {'username': 'beop_798', 'password': 'RNB.beop-2020', 'url': 'http://localhost:5002', 'timeout': 30}

    #dict_config = {'username': '_sample', 'password': 'RNB.-2020', 'url': 'http://192.168.1.48:5002','timeout': 30}
    #dict_config = {'username': '_943', 'password': 'RNB.-2020', 'url': 'http://192.168.1.48:5002','timeout': 30}
    #dict_point = {'10_Root_ModbusRTUEM_003_MSB1_G3_G4Voltages_VL_Lsys10': {'name': '10_Root_ModbusRTUEM_003_MSB1_G3_G4Voltages_VL_Lsys10', 'point_writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/10_Root_ModbusRTUEM_003_MSB1_G3_G4Voltages_VL_Lsys10/', 'type': 'real', 'description': '10_Root_ModbusRTUEM_003_MSB1_G3_G4Voltages_VL_Lsys10', 'val': '421.9'}, '10_Root_ModbusRTUEM_006_MSB1_B1Voltages_VL_Lsys10': {'name': '10_Root_ModbusRTUEM_006_MSB1_B1Voltages_VL_Lsys10', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/10_Root_ModbusRTUEM_006_MSB1_B1Voltages_VL_Lsys10/', 'type': 'real', 'description': '10_Root_ModbusRTUEM_006_MSB1_B1Voltages_VL_Lsys10', 'val': '421.8'}, '11_Root_ModbusRTUEM_003_MSB1_G3_G4Currents_AL111': {'name': '11_Root_ModbusRTUEM_003_MSB1_G3_G4Currents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_003_MSB1_G3_G4Currents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_003_MSB1_G3_G4Currents_AL111', 'val': '4.64'}, '11_Root_ModbusRTUEM_006_MSB1_B1Currents_AL111': {'name': '11_Root_ModbusRTUEM_006_MSB1_B1Currents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_006_MSB1_B1Currents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_006_MSB1_B1Currents_AL111', 'val': '0'}, '11_Root_ModbusRTUEM_DB_YOGA_LIGHTCurrents_AL111': {'name': '11_Root_ModbusRTUEM_DB_YOGA_LIGHTCurrents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_DB_YOGA_LIGHTCurrents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_DB_YOGA_LIGHTCurrents_AL111', 'val': '0.338'}, '11_Root_ModbusRTUEM_DB_YOGA_POWERCurrents_AL111': {'name': '11_Root_ModbusRTUEM_DB_YOGA_POWERCurrents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_DB_YOGA_POWERCurrents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_DB_YOGA_POWERCurrents_AL111', 'val': '1.7'}, '11_Root_ModbusRTUEM_HDB_G_LightCurrents_AL111': {'name': '11_Root_ModbusRTUEM_HDB_G_LightCurrents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_HDB_G_LightCurrents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_HDB_G_LightCurrents_AL111', 'val': '12.81'}, '11_Root_ModbusRTUEM_MSSB_L4_ECurrents_AL111': {'name': '11_Root_ModbusRTUEM_MSSB_L4_ECurrents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_MSSB_L4_ECurrents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_MSSB_L4_ECurrents_AL111', 'val': '0.01'}, '11_Root_ModbusRTUEM_TDB_10_1_N_LIGHTCurrents_AL111': {'name': '11_Root_ModbusRTUEM_TDB_10_1_N_LIGHTCurrents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_TDB_10_1_N_LIGHTCurrents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_TDB_10_1_N_LIGHTCurrents_AL111', 'val': '0.24'}, '11_Root_ModbusRTUEM_TDB_10_1_N_POWERCurrents_AL111': {'name': '11_Root_ModbusRTUEM_TDB_10_1_N_POWERCurrents_AL111', 'writable': True, 'url': '/obix/config/Drivers/BacnetNetwork/11_Root_ModbusRTUEM_TDB_10_1_N_POWERCurrents_AL111/', 'type': 'real', 'description': '11_Root_ModbusRTUEM_TDB_10_1_N_POWERCurrents_AL111', 'val': '4.51'}}
    #dict_config = {'username': 'Monitor', 'password': 'Yorktown123', 'url': 'http://67.200.176.210:8081', 'timeout':10}

    #dict_point = {}
    #dict_point = ObixDriver(dict_config, dict_point).search_points(call_back)
    #print(dict_point)
    #dict_point = {'BacnetNetwork_Temperature_Kitchen_UnoccOvrd_NotEqual1': {'point_writable': True, 'point_name': 'BacnetNetwork_Temperature_Kitchen_UnoccOvrd_NotEqual1', 'point_url': '/obix/config/Drivers/BacnetNetwork/Temperature_Kitchen_UnoccOvrd_NotEqual1/', 'point_type': 'real', 'point_description': 'Temperature_Kitchen_UnoccOvrd_NotEqual1', 'point_sample_value': '1'}}
    dict_point = {'Chiller_1_CHW_ENT': {'point_name': 'Chiller_1_CHW_ENT', 'point_writable': True,'point_url': '/obix/config/Drivers/AHU_10_CC_Int/', 'point_type': 'obj','point_description': '43.50 °F {ok}', 'point_sample_value': '43.5'}}
    driver = ObixDriver(dict_config, dict_point)
    while True:
        point_dict = driver.get_points()
        print(point_dict)
        time.sleep(5)
    driver._del_watch()

def test_case():
    test_all1()

    #test_get()

    #test_get()

    #test_scrap()

test_scan()