from qplay_cli.api_clients.instance_api import InstanceAPIClient
from qplay_cli.config.qplay_config import QplayConfig
from qplay_cli.api_clients.user_api import UserAPIClient
import click
import subprocess
import os


@click.group()
def machine():
    pass

@machine.command()
def launch():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    print("Enter lease time in hours")
    lease_time = input()

    response = InstanceAPIClient().launch_machine(access_token, lease_time)
    print(response['message'])

@machine.command()
def ssh():
    credentials = QplayConfig.get_credentials()
    access_token = credentials['DEFAULT']['access_token']

    info = UserAPIClient().get_info(access_token)

    if 'machine_ip' in info and info['machine_ip'] != False:
        bshCmd = 'ssh -i "{}/user-machine.pem" ubuntu@{}'.format(QplayConfig.config_path, info['machine_ip'])
        os.system(bshCmd)
    else:
        print("No live machine found, please rent a machine")