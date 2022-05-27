import random
import time
import Pyro4
from robertcommondriver.system.driver.opcda import OPCDADriver, get_sessions, get_info

#
def call_back(info:str):
    print(info)

def test_scan(dict_config, dict_point):
    opcda_driver = OPCDADriver(dict_config, dict_point)
    print(opcda_driver.search_servers())
    return opcda_driver.search_points('*', True)

def test_scrap(dict_config, dict_point):

    opcda_driver = OPCDADriver(dict_config, dict_point)

    while True:
        try:
            result_success, result_error = opcda_driver.get_points()
            if len(result_success) > 0:
                print(f"success : {len(result_success)} {result_success}")
            if len(result_error) > 0:
                print(f"fail : {len(result_error)} {result_error}")
            time.sleep(5)

            dict_result_scrap = opcda_driver.set_points({'Bucket Brigade.Int2': random.randint(1,10)})
            print(dict_result_scrap)
        except Exception as e:
            print(e.__str__())

def test_case():
    #配置项
    dict_config = {
                        'server': 'Matrikon.OPC.Simulation.1',          #server Matrikon.OPC.Simulation.1 KingView.View.1 Kepware.KEPServerEX.V5
                        'host': 'localhost',                  #'host': '192.168.1.36:8804',
                        'enabled': True,
                        'group': f'opcda1',
                        'action': '',       #
                        'read_limit': 50,
                        'update_rate': 500
                    }
    #点表
    dict_point = {}
    dict_point = test_scan(dict_config, dict_point)
    for name in dict_point.keys():
        print(name)

    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int', 'point_tag': '213Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_time'] = {'point_writable': True, 'point_name': 'static_time', 'point_tag': 'Bucket Brigade.Time', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}

    test_scrap(dict_config, dict_point)

    print()

def test():
    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        # server Matrikon.OPC.Simulation.1 KingView.View.1 Kepware.KEPServerEX.V5 OPCServer.WinCC.1
        'host': '192.168.1.172:8804',  # 'host': '192.168.1.36:8804', 192.168.2.131:8810
        'enabled': True,
        'group': f'opcda{random.randint(10, 1000)}',  #
        'read_limit': 50,
        'update_rate': 500
    }
    dict_point = {}
    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int',
                                'point_tag': '213Bucket Brigade.Int1', 'point_type': '', 'point_description': ''}
    dict_point['static_time'] = {'point_writable': True, 'point_name': 'static_time',
                                 'point_tag': 'Bucket Brigade.Time', 'point_type': '', 'point_description': ''}
    opcda_driver = OPCDADriver(dict_config, dict_point)
    print(opcda_driver.search_servers())


    # dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4', 'point_type': '', 'point_description': ''}
    # dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': 'Random.String', 'point_type': '', 'point_description': ''}
    print(opcda_driver.get_points())
    del opcda_driver


    test_scrap(dict_config, dict_point)

@Pyro4.expose
@Pyro4.callback
def call_back_1(content: str):
    print(content)

def test_service():

    dict_config = {
        'server': 'Matrikon.OPC.Simulation.1',
        # server Matrikon.OPC.Simulation.1 KingView.View.1 Kepware.KEPServerEX.V5
        'host': '192.168.1.172:8804',  # 'host': '192.168.1.36:8804',
        'enabled': True,
        'group': f'opcda1',
        'action': '',  #
        'read_limit': 50,
        'update_rate': 500
    }
    # 点表
    dict_point = {}

    dict_point['static_int'] = {'point_writable': True, 'point_name': 'static_int',
                                'point_tag': 'Bucket Brigade.Int4', 'point_type': '', 'point_description': ''}
    dict_point['static_time'] = {'point_writable': True, 'point_name': 'static_time',
                                 'point_tag': 'Bucket Brigade.Time', 'point_type': '', 'point_description': ''}
    dict_point['random_float'] = {'point_writable': True, 'point_name': 'random_float', 'point_tag': 'Random.Real4',
                                  'point_type': '', 'point_description': ''}
    dict_point['random_str'] = {'point_writable': True, 'point_name': 'random_str', 'point_tag': '123Random.String',
                                'point_type': '', 'point_description': ''}

    opcda_driver = OPCDADriver(dict_config, dict_point)

    while True:
        try:
            result_success, result_error = opcda_driver.get_points()
            if len(result_success) > 0:
                print(f"success : {len(result_success)} {result_success}")
            if len(result_error) > 0:
                print(f"fail : {len(result_error)} {result_error}")
            time.sleep(5)

            print(opcda_driver.ping_target())

            #print(get_sessions('192.168.1.36'))

            #print(get_info('192.168.1.36'))

            dict_result_scrap = opcda_driver.set_points({'static_int': random.randint(1, 10)})
            print(dict_result_scrap)
        except Exception as e:
            print(e.__str__())

    print()

test_case()