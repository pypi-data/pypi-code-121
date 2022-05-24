#
#  Copyright (c) 2018-2021 Renesas Inc.
#  Copyright (c) 2018-2021 EPAM Systems Inc.
#

import argparse
import logging
import sys
from pathlib import Path

from colorama import Fore, Style, init

from aos_prov.actions import create_new_unit
from aos_prov.actions import download_image
from aos_prov.commands.command_provision import run_provision

from aos_prov.communication.cloud.cloud_api import DEFAULT_REGISTER_PORT, CloudAPI
from aos_prov.utils import DEFAULT_USER_CERT_PATH, DEFAULT_USER_KEY_PATH
from aos_prov.utils.common import DISK_IMAGE_DOWNLOAD_URL
from aos_prov.utils.errors import CloudAccessError, BoardError, DeviceRegisterError, OnBoardingError
from aos_prov.utils.user_credentials import UserCredentials

try:
    from importlib.metadata import version  # noqa: WPS433
except ImportError:
    import importlib_metadata as version  # noqa: WPS433

_ARGUMENT_USER_CERTIFICATE = '--cert'
_ARGUMENT_USER_KEY = '--key'
_ARGUMENT_USER_PKCS12 = '--pkcs12'

_COMMAND_NEW_VM = 'vm-new'
_COMMAND_START_VM = 'vm-start'
_COMMAND_UNIT_CREATE = 'unit-new'
_COMMAND_DOWNLOAD = 'download'

_DEFAULT_USER_CERTIFICATE = str(Path.home() / '.aos' / 'security' / 'aos-user-oem.p12')

logger = logging.getLogger(__name__)


def _parse_args():
    parser = argparse.ArgumentParser(
        description="The board provisioning tool using gRPC protocol",
        epilog="Run 'aos-prov --help' for more information about commands, "
               "or 'aos-prov COMMAND --help' to see info about command about desired command")

    parser.add_argument(
        '-u',
        '--unit',
        required=False,
        help="Unit address in format IP_ADDRESS or IP_ADDRESS:PORT"
    )

    parser.add_argument(
        _ARGUMENT_USER_CERTIFICATE,
        default=DEFAULT_USER_CERT_PATH,
        help=f'User certificate file. Default: {DEFAULT_USER_CERT_PATH}')

    parser.add_argument(
        _ARGUMENT_USER_KEY,
        default=DEFAULT_USER_KEY_PATH,
        help=f'User key file. Default: {DEFAULT_USER_KEY_PATH}')

    parser.add_argument(
        '-p',
        _ARGUMENT_USER_PKCS12,
        required=False,
        help='Path to user certificate in pkcs12 format',
        dest='pkcs',
        default=_DEFAULT_USER_CERTIFICATE,
    )

    parser.add_argument(
        '--register-host',
        help='Overwrite cloud address. By default it is taken from user certificate'
    )

    parser.add_argument(
        '--register-port',
        default=DEFAULT_REGISTER_PORT,
        help=f'Cloud port. Default: {DEFAULT_REGISTER_PORT}'
    )

    parser.add_argument(
        '-w'
        '--wait-unit',
        action='store_true',
        help=f'Wait for unit.',
        dest='wait_unit'
    )

    parser.set_defaults(which=None)

    sub_parser = parser.add_subparsers(title='Commands')

    new_vm_command = sub_parser.add_parser(
        _COMMAND_NEW_VM,
        help='Create new Oracle VM'
    )
    new_vm_command.set_defaults(which=_COMMAND_NEW_VM)

    new_vm_command.add_argument(
        '--name',
        required=True,
        help='Name of the VM'
    )

    new_vm_command.add_argument(
        '--disk',
        required=False,
        help=f'Full path to the disk'
    )

    start_vm_command = sub_parser.add_parser(
        _COMMAND_START_VM,
        help='Start the VM'
    )
    start_vm_command.add_argument(
        '--name',
        required=True,
        help='Name of the VM'
    )
    start_vm_command.set_defaults(which=_COMMAND_START_VM)

    create_unit_command = sub_parser.add_parser(
        _COMMAND_UNIT_CREATE,
        help='Create and provision new VirtualBox-based unit'
    )
    create_unit_command.set_defaults(which=_COMMAND_UNIT_CREATE)

    create_unit_command.add_argument(
        '--name',
        required=True,
        help='Name of the VM'
    )

    create_unit_command.add_argument(
        '--disk',
        required=False,
        help='Full path to the disk'
    )

    create_unit_command.add_argument(
        '-p',
        _ARGUMENT_USER_PKCS12,
        required=False,
        help='Path to user certificate in pkcs12 format',
        dest='pkcs',
        default=_DEFAULT_USER_CERTIFICATE,
    )

    parser.add_argument(
        '-v',
        '--version',
        action='version',
        version=f"%(prog)s {version}")

    download_command = sub_parser.add_parser(_COMMAND_DOWNLOAD, help='Download image')
    download_command.set_defaults(which=_COMMAND_DOWNLOAD)
    download_command.add_argument(
        '-a',
        '--address',
        dest='download_address',
        help='Address to download image'
    )

    download_command.add_argument(
        '-f',
        '--force',
        action='store_true',
        help='Force overwrite existing file'
    )

    args = parser.parse_args()
    return args


def main():
    """The main entry point."""
    init()
    status = 0
    args = _parse_args()
    print(args)
    try:
        if args.which is None:
            if args.pkcs == _DEFAULT_USER_CERTIFICATE and \
                    (args.cert != DEFAULT_USER_CERT_PATH or args.key != DEFAULT_USER_KEY_PATH):
                args.pkcs = None
            uc = UserCredentials(cert_file_path=args.cert, key_file_path=args.key, pkcs12=args.pkcs)
            cloud_api = CloudAPI(uc, args.register_port)
            cloud_api.check_cloud_access()
            wait = 1
            if args.wait_unit:
                wait = 20
            run_provision(args.unit, cloud_api, wait)
        if args.which == _COMMAND_DOWNLOAD:
            url = DISK_IMAGE_DOWNLOAD_URL
            if args.download_address:
                url = args.download_address
            download_image(url, args.force)
        if args.which == _COMMAND_NEW_VM:
            from aos_prov.commands.command_vm import start_vm, forward_provisioning_ports
            create_new_unit(args.name)
            forward_provisioning_ports(args.name, forward_to_port=8089)
        if args.which == _COMMAND_START_VM:
            start_vm(args.name)
        if args.which == _COMMAND_UNIT_CREATE:
            uc = UserCredentials(cert_file_path=None, key_file_path=None, pkcs12=args.pkcs)
            cloud_api = CloudAPI(uc, args.register_port)
            cloud_api.check_cloud_access()
            create_new_unit(args.name, do_provision=True)
    except CloudAccessError as e:
        logger.error('\nUnable to provision the board with error:\n%s', str(e))
        status = 1
    except DeviceRegisterError as e:
        print(f"{Fore.RED}FAILED with error: {str(e)} {Style.RESET_ALL}")
        logger.error('Failed: %s', str(e))
        status = 1
    except BoardError as e:
        logger.error(f'{Fore.RED}Failed during communication with device with error: \n {str(e)}{Style.RESET_ALL}', )
        status = 1
    except OnBoardingError as e:
        print(f"{Fore.RED}Failed to provision the board! {Style.RESET_ALL}")
        print(f"{Fore.RED}Error: {Style.RESET_ALL}" + str(e))
        status = 1
    except (AssertionError, KeyboardInterrupt):
        sys.stdout.write('Exiting ...\n')
        status = 1

    sys.exit(status)


if __name__ == '__main__':
    main()
