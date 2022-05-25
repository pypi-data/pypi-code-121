from jnpr.junos import Device
from jnpr.junos.utils.sw import SW
from jnpr.junos.exception import ConnectError

from .models import EXECUTION_STATUS


def junos_reboot(host, device_name):
    """
	TODO: write docstrings
	"""
    
    dev = Device(
        host=host.inventory.hosts[device_name].hostname, 
        user=host.inventory.hosts[device_name].username, 
        passwd=host.inventory.hosts[device_name].password,
        port=host.inventory.hosts[device_name].port
    )
    # open a connection with the device and start a NETCONF session
    try:
        sw = SW(dev)
        print(sw.reboot())

    except ConnectError as err:
        print ("Cannot connect to device: {0}".format(err))
        return EXECUTION_STATUS["FAILED"]