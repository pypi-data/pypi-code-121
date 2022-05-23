import os
from src.NetmikoLibrary import NetmikoLibrary


def test_show_verson_brief(net_recorder, root_path):
    recorded_file = os.path.join(root_path, 'data', 'test_show_command.json')
    with net_recorder(recorded_file):
        conn = NetmikoLibrary()
        conn.open_connection('test-device', 'test-device.lab.com', 'cisco_xr', 'username', 'password')
        output = conn.cli('show version brief')
        assert 'Version 6.6.2' in output


def test_show_feature(net_recorder, root_path):
    recorded_file = os.path.join(root_path, 'data', 'test_show_feature.json')
    with net_recorder(recorded_file):
        conn = NetmikoLibrary()
        conn.open_connection('test-device', 'test-device.lab.com', 'cisco_nxos', 'username', 'password')
        output = conn.cli_json('show feature')
        assert output['TABLE_cfcFeatureCtrlTable']['ROW_cfcFeatureCtrlTable']


def test_clear_counters(net_recorder, root_path):
    recorded_file = os.path.join(root_path, 'data', 'test_clear_counters.json')
    with net_recorder(recorded_file):
        conn = NetmikoLibrary()
        conn.open_connection('efl1', 'elf01sqsccc.spoc.charterlab.com', 'cisco_xr', 'netqa', 'RobotR0cks')
        conn.clear_counters()
