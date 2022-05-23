import bluetooth
import sys
from prompt_toolkit.shortcuts import checkboxlist_dialog, yes_no_dialog
from prompt_toolkit.styles import Style
from .ImuSensor import MODE_WIRELESS, ImuSensor

prompt_style = Style.from_dict({
    'dialog': '#ffffff bg:',
    'dialog.body': '#ffffff bg:',
    'checkbox': '#ffffff',
    'checkbox-list': '#ffffff',
})


def connect():
    paired_devices = __read_paired_devices()
    if not paired_devices:
        print('No paired devices, please pair a new device')
        paired_devices = __pair_new_device()
        if not paired_devices:
            print('Still no paired devices, exiting.')
            sys.exit(1)
    sensors = []
    for device in paired_devices:
        sensor = ImuSensor(MODE_WIRELESS, device[0])
        sensors.append(sensor)
    return sensors


def __pair_new_device():
    try:
        print('Scanning...')
        devices = __search_devices()
        if len(devices) == 0:
            print('No IMUs were found, returning to menu.')
            return
        results = checkboxlist_dialog(
            title='Pair devices',
            text='Which devices would you like to pair?',
            style=prompt_style,
            values=[(device, device[1]) for device in devices]
        ).run()
        __write_paired_devices(results)
        return __read_paired_devices()

    except OSError:
        print('Please make sure Bluetooth is turned on!')
        sys.exit(1)


def __print_devices(devices):
    for i in range(len(devices)):
        print(f'[{i}] {devices[i][1]}')


def __search_devices():
    devices = [d for d in bluetooth.discover_devices(lookup_names=True) if d[1].startswith('WirelessIMU-')]
    if len(devices) == 0:
        search_again = yes_no_dialog(
            title='Search again?',
            text='No IMUs found, do you want to search again?',
            style=prompt_style,
        ).run()
        if search_again:
            return __search_devices()
    return devices


def __write_paired_devices(devices):
    if not devices: return
    with open('paireddevices', 'a+') as f:
        f.seek(0)
        paired_devices = f.readlines()
        devices = [' '.join(device)+'\n' for device in devices]
        devices = [device for device in devices if device not in paired_devices]
        f.writelines(devices)


def __read_paired_devices():
    try:
        with open('paireddevices', 'r') as f:
            paired_devices = [device[0:-1].split(' ') for device in f.readlines()]
        return paired_devices
    except FileNotFoundError:
        return []


def __delete_paired_devices(devices):
    with open('paireddevices', 'r+') as f:
        devices = [' '.join(device) + '\n' for device in devices]
        paired_devices = f.readlines()
        paired_devices = [device for device in paired_devices if device not in devices]
        f.seek(0)
        f.truncate()
        f.writelines(paired_devices)


