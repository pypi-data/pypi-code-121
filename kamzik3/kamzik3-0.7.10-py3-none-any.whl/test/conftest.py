import tempfile
from os import path

import pytest

from kamzik3.devices.deviceSession import DeviceSession


@pytest.fixture(scope="session", autouse=True)
def deviceSession():
    with tempfile.TemporaryDirectory() as root_log:
        session_config = {
            "attributes": {
                ("Log directory", "Value"): path.join(root_log, "server_log"),
                ("Resource directory", "Value"): path.join(root_log, "resources"),
                ("Allow attribute log", "Value"): False,
            }
        }
    session = DeviceSession(device_id="Device_Session", config=session_config)
    yield session
    session.stop()
