import xmltodict
import json

from jnpr.junos import Device
from lxml import etree

from ...utils.utils import print_json


def junos_ping(host, device_name, target, count='4'):
    """
	TODO: write docstrings
	"""
    
    dev = Device(
        host=host.inventory.hosts[device_name].hostname, 
        user=host.inventory.hosts[device_name].username, 
        passwd=host.inventory.hosts[device_name].password,
        port=host.inventory.hosts[device_name].port
    )
    dev.open()
    
    test=dev.rpc.ping(host=target, count=count)
    o = xmltodict.parse(etree.tostring(test))
    dev.close()

    loss_number = o['ping-results']['probe-results-summary']['packet-loss']
    ping_success = True if loss_number == '0' else False

    ping_results = {
        'ping-results': o['ping-results'],
        'summary': o['ping-results']['probe-results-summary'],
        'loss-number': o['ping-results']['probe-results-summary']['packet-loss'],
        'ping-success': ping_success,
    }
    return ping_results