import serial
from serial.tools.list_ports import comports
import logging
import os
from smartinput.helpers import wait_for_event
from smartinput.handle import handle_event
from smartinput.rgb.effects.rainbow import rainbow
from smartinput.rgb import constants
from smartinput.rgb.helpers import RGBDevice
from smartinput.server import run_in_thread
from smartinput.settings import settings_manager
import yaml


def main(config_path: str):
    with open(config_path, "r") as stream:
        config = yaml.safe_load(stream)

    hwid = config['device']

    port = None
    for device in comports():
        if device.hwid == hwid:
            port = device.device
    print(port)
    if not port:
        raise Exception(f"device with hwid {hwid} not found.")

    device = serial.Serial(baudrate=config['baudrate'], timeout=.1, port=port)

    run_in_thread(device)

    while True:
        event = wait_for_event(device)
        print(event)
        handle_event(event, config['keys'])


def run():
    logging.basicConfig()
    logging.getLogger().setLevel(logging.INFO)

    config_path = os.environ.get(
        "SMARTINPUT_CONFIG_PATH") or settings_manager.get_config_file_path()

    if not os.path.exists(config_path):
        os.makedirs(os.path.dirname(config_path), exist_ok=True)
        with open(config_path, "w") as file:
            file.write(yaml.dump({"device": "PLEASE CHANGE ME", "baudrate": 115200, "keys": {}}))

    main(config_path)
