import sounddevice as sd
from typing import Tuple, List, MutableMapping, Optional

from .constants import SAMPLING_RATE
from .log import logger
from .utils import my_assert, remove_non_ascii

try:
    HOST_API = sd.query_devices(kind='input')['hostapi']  # freeze host API at start
except sd.PortAudioError:
    HOST_API = -1  # only for unit tests


def get_device_list(config: MutableMapping[str, str], entry: str, out: bool) -> Tuple[List[str], int]:
    """
    Returns the list of available devices and the index of the currently selected device (from provided config)
    :param config: current config
    :param entry: relevant entry of the config
    :param out: whether we want out-devices or in-devices
    """
    config_device = config.get(entry, '')
    field = 'max_output_channels' if out else 'max_input_channels'
    chans = 2 if out else 1
    default_idx = sd.query_hostapis(HOST_API)['default_output_device' if out else 'default_input_device']
    devices = []
    selected = None
    default = None
    default_name = None
    for idx, device in enumerate(sd.query_devices()):
        if device['hostapi'] != HOST_API:
            continue
        if device[field] < chans:
            continue
        name = device['name'].strip()
        devices.append(name)
        sanitized_name = remove_non_ascii(name)
        if sanitized_name == config_device:
            selected = len(devices) - 1
        if idx == default_idx:
            default = len(devices) - 1
            default_name = name
    my_assert(len(devices) > 0, f"No suitable device found for {'output' if out else 'input'}.")  # TODO: improve
    if default is None:
        logger.warning("Default device not suitable; using first of the list")
        default = 0
        default_name = devices[0]
    if selected is None:
        logger.warning(f"Device from config ({remove_non_ascii(config_device)}) not in device list; switch to default")
        selected = default
        config[entry] = remove_non_ascii(default_name)
        if 'latency' in config:  # reset latency
            config['latency'] = '0'
    return devices, selected


def check_audio_config(config: MutableMapping[str, str], in_entry: str, out_entry: str):
    if HOST_API < 0:  # skip this when testing
        return
    logger.debug(f"Checking audio config. Host API is {HOST_API}")
    # fix config if needed
    get_device_list(config, in_entry, False)
    get_device_list(config, out_entry, True)
    try:
        sd.check_input_settings(device=get_device_index(config.get(in_entry, ''), False),
                                channels=1,
                                dtype='float32',
                                samplerate=SAMPLING_RATE)
        sd.check_output_settings(device=get_device_index(config.get(out_entry, ''), True),
                                 channels=2,
                                 dtype='float32',
                                 samplerate=SAMPLING_RATE)
    except sd.PortAudioError:
        logger.warning(f"Audio config invalid; resetting latency")
        if 'latency' in config:  # reset latency, preventing client to join
            config['latency'] = '0'


def get_device_index(selected_name: str, out: bool) -> Optional[int]:
    selected_name = remove_non_ascii(selected_name.strip())
    field = 'max_output_channels' if out else 'max_input_channels'
    chans = 2 if out else 1
    for i, dev in enumerate(sd.query_devices()):
        sanizized_name = remove_non_ascii(dev['name'].strip())
        if sanizized_name == selected_name and dev['hostapi'] == HOST_API and dev[field] >= chans:
            return i
    logger.error(f"Bad device name {remove_non_ascii(selected_name)}, using default")
    return None
