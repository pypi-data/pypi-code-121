#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#
import platform
import socket
import sys
from pathlib import Path
from random import randint
from shutil import copyfile

if platform.system() == 'Linux':
    sys.path.append('/usr/lib/virtualbox')
    sys.path.append('/usr/lib/virtualbox/sdk/bindings/xpcom/python/')
elif platform.system() == 'Darwin':
    sys.path.append('/Applications/VirtualBox.app/Contents/MacOS')
    sys.path.append('/Applications/VirtualBox.app/Contents/MacOS/sdk/bindings/xpcom/python/')


from aos_prov.actions import download_image
from aos_prov.utils.common import DOWNLOADS_PATH
from aos_prov.utils.errors import OnBoardingError

try:
    import virtualbox
    from virtualbox.library import StorageBus, StorageControllerType, IMachine, \
        DeviceType, AccessMode, NATProtocol, FirmwareType
except Exception:
    pass


def __create_storage_controller(machine: IMachine):
    storage_controller = machine.add_storage_controller('IDE', StorageBus.ide)
    storage_controller.controller_type = StorageControllerType.piix4
    storage_controller.use_host_io_cache = True


def __attach_disk(machine: IMachine, location):
    medium = machine.parent.open_medium(
        location,
        DeviceType.hard_disk,
        AccessMode.read_write,
        True
    )
    machine.attach_device('IDE', 0, 0, DeviceType.hard_disk, medium)


def __check_disk_exist(disk_location: str):
    disk = Path(disk_location)
    if not disk.is_file():
        raise OnBoardingError("Disk file not found")


def new_vm(vm_name: str, disk_location):
    print('Creating new virtual machine...')

    if disk_location is None:
        default_image_path = Path(DOWNLOADS_PATH / 'aos-disk.vmdk')
        if not default_image_path.is_file():
            download_image()
        disk_location = str(default_image_path)

    vbox = virtualbox.VirtualBox()
    try:
        machine = vbox.create_machine('', vm_name, ['/AosUnits'], 'Linux_64', '')
    except virtualbox.library_base.VBoxError:
        raise Exception('Such VM exist')
    machine.vram_size = 32
    machine.memory_size = 256
    machine.cpu_count = 1
    machine.firmware_type = FirmwareType.efi
    __create_storage_controller(machine)
    vbox.register_machine(machine)

    machine_folder = vbox.system_properties.default_machine_folder
    machine_config_file_name = vbox.compose_machine_filename(vm_name, '/AosUnits', '', machine_folder)
    vm_dir = Path(machine_config_file_name).parent
    disk_image = str(Path(vm_dir / 'aos-disk.vmdk').absolute())
    copyfile(disk_location, disk_image)

    with machine.create_session() as session:
        __attach_disk(session.machine, location=disk_image)
        session.machine.save_settings()

    return forward_provisioning_ports(vm_name, vm_name + 'PortForward')


def start_vm(vm_name: str):
    print('Starting virtual machine...')
    vbox = virtualbox.VirtualBox()
    machine = vbox.find_machine(vm_name)
    session = virtualbox.Session()
    vm = machine.launch_vm_process(session, "gui", [])
    vm.wait_for_completion(timeout=-1)


def forward_provisioning_ports(vm_name: str, redirect_name: str = 'provisioningPortForward', forward_to_port=None):
    if forward_to_port is None:
        forward_to_port = randint(8090, 8999)
        while _is_port_in_use(forward_to_port):
            forward_to_port = randint(8090, 8999)

    print(f'...will forward provisioning port {8089} to {forward_to_port}')
    vbox = virtualbox.VirtualBox()
    machine = vbox.find_machine(vm_name)
    session = virtualbox.Session()
    try:
        machine.lock_machine(session, virtualbox.library.LockType.write)
        mutable_machine = session.machine
        adapter = mutable_machine.get_network_adapter(0)
        adapter.nat_engine.add_redirect(redirect_name, NATProtocol(1), '', forward_to_port, '0.0.0.0', 8089)
        session.machine.save_settings()
    finally:
        session.unlock_machine()
    return forward_to_port


def delete_provisioning_ports(vm_name: str, redirect_name: str = 'provisioningPortForward'):
    vbox = virtualbox.VirtualBox()
    machine = vbox.find_machine(vm_name)
    session = virtualbox.Session()
    try:
        machine.lock_machine(session, virtualbox.library.LockType.write)
        mutable_machine = session.machine
        adapter = mutable_machine.get_network_adapter(0)
        adapter.nat_engine.remove_redirect(redirect_name)
        session.machine.save_settings()
        session.unlock_machine()
    except Exception:
        pass


def _is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0
