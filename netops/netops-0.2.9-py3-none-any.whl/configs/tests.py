from jnpr.junos import Device
from lxml import etree

from getpass import getpass
from jnpr.junos.exception import ConnectError
import sys

def device(nornir, device_name):
    """ TODO: write docstrings
    Retorna o Objeto Device com suas credenciais para ser conectado
    """
    print("host: ", nornir.inventory.hosts[device_name].hostname)
    print("user: ", nornir.inventory.hosts[device_name].username)
    print("pass: ", nornir.inventory.hosts[device_name].password)
    print("port: ", nornir.inventory.hosts[device_name].port)

    dev = Device(
        host=nornir.inventory.hosts[device_name].hostname,
        user=nornir.inventory.hosts[device_name].username,
        passwd=nornir.inventory.hosts[device_name].password,
        port=nornir.inventory.hosts[device_name].port,
    )

    return dev

def junos_pyez_get_configs(nornir=None, dev_name=None, dev=None):
    if not dev:
        dev = device(nornir, dev_name)

    data = dev.rpc.get_config(options={'database' : 'committed'})
    print (etree.tostring(data, encoding='unicode', pretty_print=True))


import os
from nornir import InitNornir

hostname = input("Device hostname: ")
junos_username = input("Junos OS username: ")
junos_password = getpass("Junos OS or SSH key password: ")
"""
try:
    with Device(host=hostname, user=junos_username, passwd=junos_password) as dev:
        print (dev.facts)
except ConnectError as err:
    print ("Cannot connect to device: {0}".format(err))
    sys.exit(1)
except Exception as err:
    print (err)
    sys.exit(1)
"""

script_dir = os.path.dirname(os.path.realpath(__file__))

nr = InitNornir(config_file=f"{script_dir}/config.yml")

#junos_pyez_get_configs(nr, 'access')
try:
    with Device(host=hostname, user=junos_username, passwd=junos_password) as dev:
        junos_pyez_get_configs(dev=dev)
except ConnectError as err:
    print ("Cannot connect to device: {0}".format(err))
    sys.exit(1)
except Exception as err:
    print (err)
    sys.exit(1)