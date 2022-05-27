from slugify import slugify
from nornir.core.exceptions import ConnectionNotOpen, NornirExecutionError

from netops.utils.utils import print_json
from .models import (PORT_MAPPING_DB, PORTS_TABLE, INVALID_JUNOS_CONFIG_STATEMENTS, PORTS_COLUMN_NAMES)
from ..utils.databases import (
    create_db,
    create_table_in_db,
    put_data_db,
    get_values_from_table
)
from ..configs.get_configs import (
    junos_pyez_get_configs,
    junos_pyez_convert_configs_2_list,
    junos_pyez_get_interfaces
)
from ..configs.models import pyez_device
from ..api.netbox.netbox_manager import NetboxManager
from ..api.netbox.util import get_sot_filter_parameters


def gen_junos_interfaces_list(int_number):
    """
    Generates list of interface names of Junos device.

    Input:
            int_number: maximum number of interfaces of emulated device
    Output:
            interface_list: list of available interface names
    """
    default_int_name = 'ge-0/0/'
    interface_list = []
    for i in range(int_number):
        interface_name = default_int_name+str(i)
        interface_list.append(interface_name)
    return interface_list


def get_interface(int_list):
    """
    Get interface from list of interface names.

    Input:
            int_list: list of interfaces
    Output:
            name of interface
    """
    return int_list.pop(0)


def create_port_map_db(dev_name):
    """
    Create port mapping interface database (DB) and table in DB.
    """
    db_name = get_port_map_db_name(dev_name)
    create_db(db_name)
    table_values = {
        'po_interface': 'TEXT',
        'lo_interface': 'TEXT',
    }
    create_table_in_db(db_name, PORTS_TABLE, table_values)
    return


def get_port_map_db_name(dev_name):
    """
    Get port mapping database name based on device name.

    Input:
            dev_name: name of the device
    Ouput:
            port_map_db_name: name of the port_map_db_name
    """
    slug = slugify(dev_name)
    port_map_db_name = f"{PORT_MAPPING_DB}-{slug}.db"
    return port_map_db_name
    

def map_po_2_lo_configs(configs_list, port_map):
    """
    Maps configuration statements <configs_list> from Physical Object to Logical Object 
    (based on <port_map>).

    Input:
            configs_list: list of configuration statements from Physical Object
            port_map: list of tuples of port mapping (id, po_interface, lo_interface, ...)
    Output:
            configs_list: list of configuration statement to Logical Object
    """
    po_interfaces = []
    lo_interfaces = []
    for map in port_map['values']:
        po_interfaces.append(map[1])
        lo_interfaces.append(map[2])
    stat_pos = 0
    for statement in configs_list:
        change_statement = False
        po_int_pos = 0
        for int_name in po_interfaces:
            if int_name in statement:
                change_statement = True
                change_po_int = po_int_pos
            po_int_pos += 1
        if change_statement:
            configs_list[stat_pos] = configs_list[stat_pos].replace(
                po_interfaces[change_po_int], 
                lo_interfaces[change_po_int]
            )
        stat_pos += 1
    return configs_list


def get_junos_lo_configs_from_nornir(nornir, dev_name):
    # Get device configes in default mode (XML like)
    device_configs = junos_pyez_get_configs(nornir=nornir, dev_name=dev_name, get_print=False, format=None)
    # Get device configes in set mode
    device_configs_set = junos_pyez_get_configs(nornir=nornir, dev_name=dev_name, get_print=False, format='set')
    # Convert set statements to a list of statements making STATEMENTS MAPPING
    po_clist = junos_pyez_convert_configs_2_list(device_configs_set, INVALID_JUNOS_CONFIG_STATEMENTS)
    print_json(po_clist)

    # Get interface names of Physical Object
    po_int = junos_pyez_get_interfaces(device_configs)

    # Generate interface names for Logical Objets
    avail_lo_int = gen_junos_interfaces_list(64)

    # Create PORT MAPPING database
    create_port_map_db(dev_name)
    
    # Get PORT MAPPING database name
    pm_db_name = get_port_map_db_name(dev_name)

    # Populate PORT MAPPING database with lo-interface and po-interface pairs
    data = []
    for i in range(len(po_int)):
        data.append( (i, get_interface(po_int), get_interface(avail_lo_int)) )
    put_data_db(pm_db_name, PORTS_TABLE, PORTS_COLUMN_NAMES, data)

    # Get all values in PORT MAPPING DATABASE
    values = get_values_from_table(pm_db_name, PORTS_TABLE)
    print_json(values)

    # Convert Physical Objects configs to Logical Objects configs based on PORT MAPPING database
    lo_clist = map_po_2_lo_configs(po_clist, values)
    print('============================== New LO configs: ')
    print_json(lo_clist)

    return lo_clist


def get_junos_lo_configs(nornir=None, dev_name=None, dev=None):
    """
    Get Junos device configs using Juniper PYEZ library.

    Input:
            nornir: nornir object
            dev_name: device name equal to the name available in nornir inventory
            dev: junos pyez device (used just if nornir and dev_name are not specified)
    Output:
            Logical Object (LO) config statements
    """
    # When device is not directly given as an input
    if not dev:
        device = pyez_device(nornir, dev_name)
    # When device is directly given as input
    else:
        device = dev

    # Get Physical Object (PO) config statements
    device_configs = junos_pyez_get_configs(dev=device, get_print=False, format=format)
    device_configs_set = junos_pyez_get_configs(dev=device, get_print=False, format='set')

    # Statements mapping
    po_clist = junos_pyez_convert_configs_2_list(device_configs_set, INVALID_JUNOS_CONFIG_STATEMENTS)

    # Get PO interface names
    po_int = junos_pyez_get_interfaces(device_configs)
    # Get LO available interface names
    avail_lo_int = gen_junos_interfaces_list(64)
    # Create port map database
    create_port_map_db()
    column_names = PORTS_COLUMN_NAMES
    data = []
    for i in range(len(po_int)):
        data.append( (i, get_interface(po_int), get_interface(avail_lo_int)) )
    put_data_db(PORT_MAPPING_DB, PORTS_TABLE, column_names, data)
    tb_values = get_values_from_table(PORT_MAPPING_DB, PORTS_TABLE)

    # Port mapping
    lo_clist = map_po_2_lo_configs(po_clist, tb_values)

    return '\n'.join(lo_clist)


"""
def get_lo_configs():
    try:
        filter_params = get_sot_filter_parameters()
        netbox_manager = NetboxManager(filter_params=filter_params)
    except NornirExecutionError as e:
        print("Error NornirExecutionError !", str(e))
    except Exception as e:
        print("Error!", str(e))

    nr_inv = netbox_manager.get_nornir()
    for host in nr_inv:
        from 
"""
