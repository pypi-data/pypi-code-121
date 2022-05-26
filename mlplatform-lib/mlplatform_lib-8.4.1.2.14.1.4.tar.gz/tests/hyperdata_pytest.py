from mlplatform_lib.hyperdata.hyperdata_checker import HyperdataChecker

import pytest


@pytest.mark.usefixtures("get_server_config_path")
def test_pre_check_hyperdata(get_server_config_path):
    server_config_path = get_server_config_path
    pre_check_base = HyperdataChecker(server_config_path=server_config_path)
    pre_check_base.run()
