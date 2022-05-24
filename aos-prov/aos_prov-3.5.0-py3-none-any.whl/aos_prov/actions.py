#
#  Copyright (c) 2018-2022 Renesas Inc.
#  Copyright (c) 2018-2022 EPAM Systems Inc.
#
import os
import platform
import subprocess
import time
import zipfile
from pathlib import Path

from aos_prov.commands.command_provision import run_provision
from aos_prov.commands.download import download_and_save_file
from aos_prov.communication.cloud.cloud_api import CloudAPI
from aos_prov.utils.common import DOWNLOADS_PATH, AOS_DISK_PATH
from aos_prov.utils.user_credentials import UserCredentials


def create_new_unit(vm_name, do_provision=False):
    uc = UserCredentials(cert_file_path=None,
                         key_file_path=None,
                         pkcs12=str(Path.home() / '.aos' / 'security' / 'aos-user-oem.p12'))
    cloud_api = CloudAPI(uc)
    cloud_api.check_cloud_access()
    if platform.system() == 'Linux':
        # from aos_prov.command_vm_libvirt import create_libvirt_vm
        # unit_uuid, vm_port = create_libvirt_vm(vm_name, None)
        from aos_prov.commands.command_vm import new_vm, start_vm
        vm_port = new_vm(vm_name, None)
        start_vm(vm_name)
    elif platform.system() == 'Darwin':
        from aos_prov.commands.command_vm_libvirt import create_libvirt_vm
        unit_uuid, vm_port = create_libvirt_vm(vm_name, None)
    elif platform.system() == 'Windows':
        from aos_prov.commands.command_vm_libvirt import create_libvirt_vm
        unit_uuid, vm_port = create_libvirt_vm(vm_name, None)
    if do_provision:
        time.sleep(10)
        run_provision(f'127.0.0.1:{vm_port}', cloud_api, reconnect_times=20)


def download_image(download_url: str, force: bool = False):
    download_and_save_file(download_url, AOS_DISK_PATH, force)


def install_vbox_sdk():
    file = download_vbox_sdk()

    with zipfile.ZipFile(file, 'r') as zip_ref:
        zip_ref.extractall(DOWNLOADS_PATH)

    envs = os.environ.copy()
    if platform.system() == 'Windows':
        command = ['python', 'vboxapisetup.py', 'install', '--user']
    elif platform.system() == 'Linux':
        'VBOX_INSTALL_PATH=$(which virtualbox)'
        command = ['python3', 'vboxapisetup.py', 'install', '--user', '--prefix=']
    elif platform.system() == 'Darwin':
        'VBOX_INSTALL_PATH=/Applications/VirtualBox.app/Contents/MacOS'
        command = ['python3', 'vboxapisetup.py', 'install', '--user', '--prefix=']
    else:
        command = 'VBOX_INSTALL_PATH=$(which virtualbox) python3 vboxapisetup.py install --user --prefix='
    return_code = subprocess.run(command, shell=True, env=envs, cwd=str(Path(DOWNLOADS_PATH / 'sdk' / 'installer')))
    if return_code.returncode == 0:
        return
    else:
        print('Error installing VirtualBox SDK')
