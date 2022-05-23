from os import path
import time
from src.NetmikoLibrary import NetmikoLibrary


def test_show_verson_brief(net_recorder, root_path):

    test_file = path.join(root_path, 'data', 'test_push_config.json')
    jinja_file = path.join(root_path, 'data', 'telemetry.jinja2')
    yaml_file = path.join(root_path, 'data', 'telemetry.yaml')

    with net_recorder(test_file):
        conn = NetmikoLibrary()
        conn.open_connection('test-device', 'test-device.lab.com', 'cisco_xr', 'username', 'password')
        cfg_commands = conn.generate_config(jinja_file, yaml_file)
        output = conn.push_config(cfg_commands)
        output = conn.cli('show telemetry model-driven subscription Sub1')
        assert '127.0.0.1' in output
