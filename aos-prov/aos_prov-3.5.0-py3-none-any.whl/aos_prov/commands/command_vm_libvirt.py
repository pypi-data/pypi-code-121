import os
import socket
import sys
import uuid
import random
from pathlib import Path
from shutil import copyfile

import libvirt

import importlib_resources as pkg_resources

from aos_prov.command_download import download_image

__FILES_DIR = 'aos_prov'
__VM_FILENAME = 'files/vm.xml'

_DOWNLOADS_PATH = Path.home() / '.aos' / 'downloads'
_VIRT_UNITS_PATH = Path.home() / '.aos' / 'virtual-units'

_IMG_FILE_NAME = 'aos-disk.vmdk'


def random_mac():
    mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    return ':'.join(map(lambda x: "%02x" % x, mac))


def _is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


def create_libvirt_vm(name: str, forward_to_port=None):
    vm_config = pkg_resources.files(__FILES_DIR) / __VM_FILENAME
    with pkg_resources.as_file(vm_config) as config:
        with open(config, 'r') as f:
            xml_config = f.read()

    new_uuid = str(uuid.uuid4())
    mac_address = random_mac()
    new_vm_path = str(_VIRT_UNITS_PATH / name / _IMG_FILE_NAME)
    if not Path(_DOWNLOADS_PATH / _IMG_FILE_NAME).exists():
        download_image()
    Path(_VIRT_UNITS_PATH / name).mkdir(parents=True, exist_ok=False)

    copyfile(str(_DOWNLOADS_PATH / _IMG_FILE_NAME), new_vm_path)

    if forward_to_port is None:
        forward_to_port = random.randint(8090, 8999)
        while _is_port_in_use(forward_to_port):
            forward_to_port = random.randint(8090, 8999)

    xml_config = xml_config.format(
        vm_name=name,
        uuid=new_uuid,
        disk_path=new_vm_path,
        mac_address=mac_address,
        port_forward=forward_to_port
    )

    try:
        conn = libvirt.open("qemu:///system")
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    try:
        dom = conn.defineXMLFlags(xml_config, 0)
    except libvirt.libvirtError as e:
        print(repr(e), file=sys.stderr)
        exit(1)

    if dom.create() < 0:
        print('Can not boot guest domain.', file=sys.stderr)
        exit(1)

    return new_uuid, forward_to_port
