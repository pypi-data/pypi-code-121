from pprint import pformat

import click
from click_didyoumean import DYMGroup
from huawei_lte_api.Client import Client
from huawei_lte_api.enums.device import ControlModeEnum

from .root import cli
from ..core.connection import HRC_Connection


@cli.group(cls=DYMGroup)
def device():
    """ Device commands """
    pass


@device.command('info')
def device_info():
    """ Get device information """
    try:
        with HRC_Connection() as conn:
            client = Client(conn)
            device_info_str = pformat(
                client.device.information()
            )
    except Exception as e:
        msg = 'Can not get device information, reason: "{}"' \
              .format(e)
    else:
        msg = device_info_str

    click.echo(msg)


@device.command('reboot')
def device_reboot():
    """ Reboot the router without any confirmation prompts """
    try:
        with HRC_Connection() as conn:
            Client(conn).device.set_control(ControlModeEnum.REBOOT)
    except Exception as e:
        msg = 'Execution failed, reason: "{}"'.format(e)
    else:
        msg = 'Rebooting the device, router will restart in several moments'

    click.echo(msg)
