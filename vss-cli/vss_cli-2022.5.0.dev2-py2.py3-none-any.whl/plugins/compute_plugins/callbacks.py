"""Compute Callback module for VSS CLI (vss-cli)."""
import json
from pathlib import Path
from typing import Optional, Tuple

from click.exceptions import BadArgumentUsage, BadParameter
from ruamel.yaml import YAML
from ruamel.yaml.scanner import ScannerError

from vss_cli.autocompletion import _init_ctx
from vss_cli.config import Configuration
from vss_cli.helper import to_tuples


def process_networks_opt(ctx: Configuration, param, value):
    """Process network option."""
    _init_ctx(ctx)
    if value is not None:
        networks = list()
        for nic in value:
            _nic = to_tuples(nic)[0]
            _network = _nic[0]
            if len(_nic) > 1:
                _type = ctx.client.get_vm_nic_type_by_name(_nic[1])
                _type = _type[0]['type']
            else:
                _type = 'vmxnet3'
            _net = ctx.client.get_network_by_name_or_moref(_network)
            networks.append({'network': _net[0]['moref'], 'type': _type})
        return networks


def process_scsi_opt(ctx: Configuration, param, value):
    """Process SCSI spec option.

    <type>=<sharing>

     or

    {
     "type": "paravirtual",
     "sharing": "nosharing",
     "bus": 0,
    }
    """
    _init_ctx(ctx)
    if value is not None:
        devices = list()
        _sharing = 'nosharing'
        for dev in value:
            scsi = {}
            try:
                _dev = json.loads(dev)
                if not isinstance(_dev, dict):
                    raise BadParameter(
                        'Must be an object with at least the type attribute'
                    )
                is_json = True
            except ValueError:
                is_json = False
                _dev = to_tuples(dev)[0]
            # get values either from tuple or dict
            try:
                if is_json:
                    _type = _dev['type']
                else:
                    _type = _dev[0]
                # lookup device type
                _type = ctx.client.get_vm_scsi_type_by_name(_type)
                _type = _type[0]['type']
                scsi['type'] = _type
            except KeyError:
                raise BadParameter('at least type must be provided')

            if is_json:
                if _dev.get('sharing') is not None:
                    _sharing = ctx.client.get_vm_scsi_sharing_by_name(
                        _dev.get('sharing')
                    )
                    _sharing = _sharing[0]['type']
                    scsi['sharing'] = _sharing
                if _dev.get('bus') is not None:
                    try:
                        _bus = int(_dev['bus'])
                    except ValueError:
                        raise BadParameter('bus must be a number')
                    scsi['bus'] = _bus
            else:
                if len(_dev) > 1:
                    _sharing = ctx.client.get_vm_scsi_sharing_by_name(_dev[1])
                    _sharing = _sharing[0]['type']
                    scsi['sharing'] = _sharing
                else:
                    scsi['sharing'] = _sharing
            devices.append(scsi)
        return devices


def process_disk_opt(ctx: Configuration, param, value):
    """Process Disk spec option.

    <capacity>=<backing_mode>=<backing_sharing>=<backing_vmdk>

     or

    {
     "capacity_gb": 100,
     "backing_mode": "persistent",
     "backing_sharing": "sharingnone",
     "backing_vmdk": "[vssUser-xfers] vskey/user/disk-0.vmdk",
     "scsi": 1
    }
    """
    _init_ctx(ctx)
    if value is not None:
        devices = list()
        _backing_mode = 'persistent'
        _sharing_mode = 'sharingnone'
        for dev in value:
            disk = {}
            try:
                _dev = json.loads(dev)
                if not isinstance(_dev, dict):
                    raise ValueError(
                        'Must be an object with at least capacity_gb'
                    )
                is_json = True
            except ValueError:
                is_json = False
                _dev = to_tuples(dev)[0]

            try:
                if is_json:
                    _capacity = int(_dev['capacity_gb'])
                else:
                    _capacity = int(_dev[0])
                disk['capacity_gb'] = _capacity
            except ValueError:
                raise BadParameter('capacity must be a number')
            if is_json:
                if _dev.get('backing_mode'):
                    _backing_mode = ctx.client.get_vm_disk_backing_mode_by_name(  # NOQA:
                        _dev.get('backing_mode')
                    )
                    _backing_mode = _backing_mode[0]['type']
                    disk['backing_mode'] = _backing_mode
                if _dev.get('backing_sharing'):
                    _sharing_mode = ctx.client.get_vm_disk_backing_sharing_by_name(  # NOQA:
                        _dev.get('backing_sharing')
                    )
                    _sharing_mode = _sharing_mode[0]['type']
                    disk['backing_sharing'] = _sharing_mode
                if _dev.get('backing_vmdk'):
                    _backing_vmdk = ctx.client.get_vmdk_by_name_path_or_id(
                        _dev.get('backing_vmdk')
                    )
                    disk['backing_vmdk'] = _backing_vmdk[0]['path']
                if _dev.get('scsi') is not None:
                    try:
                        _scsi_crllr = int(_dev.get('scsi'))
                    except ValueError:
                        raise BadParameter('scsi must be a number')
                    disk['scsi'] = _scsi_crllr
            else:
                if len(_dev) > 1:
                    _spec = to_tuples(_dev[1])[0]
                    if len(_spec) > 0:
                        _backing_mode = ctx.client.get_vm_disk_backing_mode_by_name(  # NOQA:
                            _spec[0]
                        )
                        _backing_mode = _backing_mode[0]['type']
                        disk['backing_mode'] = _backing_mode
                    if len(_spec) > 1:
                        _spec = to_tuples(_spec[1])[0]
                        _sharing_mode = ctx.client.get_vm_disk_backing_sharing_by_name(  # NOQA
                            _spec[0]
                        )
                        _sharing_mode = _sharing_mode[0]['type']
                        disk['backing_sharing'] = _sharing_mode
                    if len(_spec) > 1:
                        _backing_vmdk = ctx.client.get_vmdk_by_name_path_or_id(
                            _spec[1]
                        )
                        _backing_vmdk = _backing_vmdk[0]['path']
                        disk['backing_vmdk'] = _backing_vmdk
            devices.append(disk)
        return devices


def process_options(ctx: Configuration, param, key_value):
    """Process options."""
    _init_ctx(ctx)
    try:
        _options = to_tuples(','.join(key_value))
        options = [{opt[0]: opt[1]} for opt in _options]
        return options
    except Exception:
        raise BadArgumentUsage(f'{param} must be key=value strings')


def process_firmware(ctx: Configuration, param, value):
    """Process firmware options."""
    _init_ctx(ctx)
    try:
        _firmware = ctx.client.get_vm_firmware_by_type_or_desc(value)
        return _firmware[0]['type']
    except Exception:
        valid = ctx.client.get_supported_firmware_types()
        raise BadArgumentUsage(f'{param} must be one of: {", ".join(valid)}')


def process_user_data(
    ctx: Configuration, param, value
) -> Optional[Tuple[str, str]]:
    """Process user_data."""
    from pyvss.helper import compress_encode_string

    _init_ctx(ctx)
    if value:
        try:
            fp = Path(value)
            txt = fp.read_text()
            _ = YAML().load(txt)
            return (
                compress_encode_string(txt),
                'gzip+base64',
            )
        except FileNotFoundError:
            raise BadArgumentUsage(f'{param} must a valid file path.')
        except ScannerError as ex:
            raise BadParameter(f'Invalid yaml provided: {str(ex)}')
