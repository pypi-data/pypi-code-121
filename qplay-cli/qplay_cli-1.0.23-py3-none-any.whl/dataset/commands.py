from qplay_cli.dataset.volume import Volume
import click
from qplay_cli.config.qplay_config import QplayConfig
from qplay_cli.api_clients.user_api import UserAPIClient
import os

@click.group()
def dataset():
    pass

@dataset.command()
def list_xvd_disks():
    vol = Volume()
    print(vol.list_xvd_disks())

@dataset.command()
@click.option('--nvme_device', default=None)
def list_nvme_volumes(nvme_device):
    vol = Volume()
    print(vol.list_nvme_volumes(nvme_device))

@dataset.command()
@click.option('--dataset_type', default=None)
def mount_dataset(dataset_type):
    vol = Volume()
    vol.mount_dataset(dataset_type)

@dataset.command()
def unmount_datasets():
    vol = Volume()
    vol.unmount_datasets()

@dataset.command()
@click.option('--files', default=None)
def download_data(files):
    if not files:
        raise Exception("must provide files")
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    info = UserAPIClient().get_info(access_token)

    files = files.split(",")
    for file in files:
        if 'machine_ip' in info and info['machine_ip'] != False:
            scp_command = 'scp -r -i "{}//user-machine.pem" ubuntu@{}:/NSE_OPT/minute/{} {}/NSE_OPT/minute'
            scp_command = scp_command.format(QplayConfig.config_path, info['machine_ip'], file, QplayConfig.config_path)
            os.system(scp_command)
        else:
            print("No live machine found, please rent a machine")