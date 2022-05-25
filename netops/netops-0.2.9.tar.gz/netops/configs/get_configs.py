from lxml import etree
from jnpr.junos.exception import ConnectError

from ..utils.utils import (
    print_json,
    elem2dict
)
from .models import pyez_device

def junos_pyez_get_configs(nornir=None, dev_name=None, dev=None, get_print=False, format=None, filter_xml=None, model=True):
    d_data = None
    if not dev:
        device = pyez_device(nornir, dev_name)
        try:
            device.open()
        except ConnectError as err:
            print ("Cannot connect to device: {0}".format(err))
            exit(1)
        except Exception as err:
            print(err)
            exit(1)
    else:
        device = dev
    options_default={'database' : 'committed'}
    options_custom = {}
    # XML format (default), Text format, Junos OS set format or JSON format
    if format:
        if format.lower() in ['text', 'set', 'json']:
            options_custom={ 'format': format.lower() }

    options={**options_default, **options_custom}

    if model in ['ietf', 'openconfig', 'custom', True]:
        model=model
    else:
        exit(1)

    if model == True:
        data = device.rpc.get_config(model=True, options=options)
    else:
        data = device.rpc.get_config(filter_xml=filter_xml, model=model, options=options)
    if not dev:
        device.close()

    if format:
        if format.lower() in ['json']:
            data_str = data
        else:
            data_str = etree.tostring(data, encoding='unicode', pretty_print=True)
    else: #default case
        print("XML: ", data)
        d_data = elem2dict(data)
        data_str = etree.tostring(data, encoding='unicode', pretty_print=True)

    if get_print:
        if d_data:
            print_json(d_data)
        else:
            print_json(data_str)

    if d_data:
        return d_data
    else:
        return data_str


def junos_pyez_get_interfaces(config_dict):
    """
    Get configured interfaces from configuration dictionary <config_dict>.

    Input:
            config_dict: junos pyez configuration dictionary (json-like)
    Output:
            interfaces: list of configured interface names
    """
    interfaces = []
    for interface in config_dict['configuration']['interfaces']['interface']:
        interfaces.append(interface['name'])
    return interfaces


def junos_pyez_convert_configs_2_list(config_str, comp_strings):
    """
    Convert a multiline configuration string to a valid config statements list

    Input:
            config_str: multiline configuration string
            comp_strings: comparison strings that are not valid in config statement
    Output:
            config_list: list of valid configuration statements
    """
    config_lines = config_str.splitlines()
    configs_list = []
    for line in config_lines:
        valid_config = True
        for str_comp in comp_strings:
            if str_comp in line:
                valid_config = False
        if valid_config:
            configs_list.append(line)
    return configs_list
