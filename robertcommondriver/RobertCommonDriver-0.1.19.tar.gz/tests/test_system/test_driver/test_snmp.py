import time
from robertcommondriver.system.driver.snmp import SNMPDriver

def print_value(value):
    print(value)


def test_all():
    dict_config = {
        "device_host": "192.168.1.200:161",
        "cmd_timeout": 3,
        "cmd_retries": 3,
        "cmd_interval": 0.3,
        "multi_read": 20,
        "root_oid": "1.3",
        # "context_name": "",
        # "context_id": "",
        "auth": {
            "v2": {"read_community": "public", "write_community": "private"}
            # "v2": {"read_community": "public", "write_community": "private"},
            # "v3": {"use_name": "", "security_level": 0, "auth_key": "", "priv_key": "", "auth_protocol": 0, "priv_protocol": 0}
        }
    }

    dict_point = {}
    dict_point['plc1'] = {'point_writable': True, 'point_name': 'snmp0', 'point_oid': '1.3.6.1.2.1.1.1.0'}
    dict_point['plc2'] = {'point_writable': True, 'point_name': 'snmp1', 'point_oid': '1.3.6.1.2.1.1.2.0'}
    dict_point['plc3'] = {'point_writable': True, 'point_name': 'snmp2', 'point_oid': '1.3.6.1.2.1.1.3.0'}
    dict_point['plc4'] = {'point_writable': True, 'point_name': 'snmp3', 'point_oid': '1.3.6.1.2.1.1.4.0'}

    driver = SNMPDriver(dict_config, dict_point)

    driver.search_points(print_value)

    while True:
        point_dict = driver.get_points()
        print(point_dict)
        time.sleep(5)


def test_case():
    test_all()


test_case()