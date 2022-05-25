"""Compute VM plugin for VSS CLI (vss-cli)."""
import datetime
import logging
import os
from typing import Optional

import click
from click_plugins import with_plugins
from pkg_resources import iter_entry_points

from vss_cli import const, rel_opts as so
import vss_cli.autocompletion as autocompletion
from vss_cli.cli import pass_context
from vss_cli.config import Configuration
from vss_cli.exceptions import VssCliError
from vss_cli.helper import format_output, raw_format_output, to_tuples
from vss_cli.plugins.compute import cli
from vss_cli.plugins.compute_plugins import rel_args as c_sa, rel_opts as c_so
from vss_cli.plugins.compute_plugins.helper import process_retirement_new
from vss_cli.validators import (
    flexible_email_args, retirement_value, validate_email, validate_json_type,
    validate_phone_number)

_LOGGING = logging.getLogger(__name__)


@with_plugins(iter_entry_points('vss_cli.contrib.compute.vm'))
@cli.group('vm', short_help='Manage virtual machines')
@pass_context
def compute_vm(ctx: Configuration):
    """List, update, deploy and delete instances."""
    pass


@compute_vm.command('ls', short_help='List virtual machine')
@so.filter_opt
@so.all_opt
@so.page_opt
@so.sort_opt
@so.count_opt
@pass_context
def compute_vm_ls(
    ctx: Configuration,
    filter_by,
    show_all: bool,
    sort,
    page,
    count,
):
    """List virtual machine instances.

    Filter and sort list by any attribute. For example:

    vss-cli compute vm ls -f name=like,%vm-name% -f version=like,%13

    Simple name filtering:

    vss-cli compute vm ls -f name=%vm-name% -s name=desc

    """
    params = dict(expand=1, sort='name,asc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # get templates
    with ctx.spinner(disable=ctx.debug):
        obj = ctx.get_vms(show_all=show_all, per_page=count, **params)
    # including additional attributes?
    columns = ctx.columns or const.COLUMNS_VM
    # format output
    output = format_output(ctx, obj, columns=columns)
    # page
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@compute_vm.group(
    'get',
    short_help='Get virtual machine info.',
    invoke_without_command=True,
)
@click.argument(
    'vm_id_or_name',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.virtual_machines,
)
@pass_context
def compute_vm_get(ctx: Configuration, vm_id_or_name):
    """Obtain virtual machine summary and other attributes."""
    _vm = ctx.get_vm_by_id_or_name(vm_id_or_name)
    ctx.moref = _vm[0]['moref']
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_VM_INFO
        obj = ctx.get_vm(ctx.moref)
        if not obj:
            raise VssCliError('Virtual Machine not found')
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('admin', short_help='Admin (metadata)')
@pass_context
def compute_vm_get_admin(
    ctx: Configuration,
):
    """Virtual machine administrator. Part of the VSS metadata."""
    columns = ctx.columns or const.COLUMNS_VM_ADMIN
    obj = ctx.get_vm_vss_admin(ctx.moref)
    if not obj:
        raise VssCliError('Virtual Machine Admin not found')
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('alarm', short_help='Triggered alarms')
@click.argument('moref', type=click.STRING, required=False)
@pass_context
def compute_vm_get_alarms(ctx: Configuration, moref):
    """Virtual machine triggered alarms."""
    if moref:
        columns = ctx.columns or const.COLUMNS_VM_ALARM
        obj = ctx.get_vm_alarm(ctx.moref, moref)
        obj = obj or []
        ctx.echo(format_output(ctx, obj, columns=columns, single=True))
    else:
        columns = ctx.columns or const.COLUMNS_VM_ALARM
        obj = ctx.get_vm_alarms(ctx.moref)
        obj = obj or []
        ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('boot', short_help='Boot configuration')
@pass_context
def compute_vm_get_boot(
    ctx: Configuration,
):
    """Virtual machine boot settings.

    Including boot delay and whether or not
    to boot and enter directly to BIOS.
    """
    columns = ctx.columns or const.COLUMNS_VM_BOOT
    obj = ctx.get_vm_boot(ctx.moref)
    obj = obj or {}
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('cd', short_help='CD/DVD configuration')
@click.argument('unit', type=int, required=False)
@pass_context
def compute_vm_get_cds(ctx: Configuration, unit):
    """Virtual machine CD/DVD configuration."""
    if unit:
        obj = ctx.get_vm_cd(ctx.moref, unit)
        if obj:
            columns = ctx.columns or const.COLUMNS_VM_CD
            ctx.echo(format_output(ctx, obj, columns=columns, single=True))
        else:
            logging.error('Unit does not exist')
    else:
        devs = ctx.get_vm_cds(ctx.moref)
        obj = [d.get('data') for d in devs] if devs else []
        columns = ctx.columns or const.COLUMNS_VM_CD_MIN
        ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('cr', short_help='Change Requests')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def compute_vm_get_cr(
    ctx: Configuration, filter_by, page, sort, show_all, count
):
    """Get associated Vm Change Requests.

    Filter list in the following format <field_name>=<operator>,<value>
    where operator is eq, ne, lt, le, gt, ge, like, in.
    For example: status=eq,Processed

    vss-cli compute vm get <id> cr -f attribute=name

    Sort list in the following format <field_name>=<asc|desc>. For example:

    vss-cli compute vm get <id> cr -s created_on=desc
    """
    columns = ctx.columns or const.COLUMNS_REQUEST_CHANGE_MIN_VM
    params = dict(expand=1, sort='created_on,desc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_vm_change_requests(
            ctx.moref, show_all=show_all, per_page=count, **params
        )

    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@compute_vm_get.command('client', short_help='Client (Metadata)')
@pass_context
def compute_vm_get_client(ctx: Configuration):
    """Get current virtual machine client department.

    Part of the VSS metadata.
    """
    obj = ctx.get_vm_vss_client(ctx.moref)
    columns = ctx.columns or [('value',)]
    obj = obj or {}
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('client-note', short_help='Client note (Metadata)')
@pass_context
def compute_vm_get_client_notes(ctx):
    """Virtual machine client notes. Part of the VM metadata."""
    obj = ctx.get_vm_notes(ctx.moref)
    columns = ctx.columns or [('value',)]
    obj = obj or {}
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('console', short_help='Virtual machine console link')
@click.option(
    '-l', '--launch', is_flag=True, help='Launch link to default handler'
)
@click.option(
    '-c',
    '--client',
    type=click.Choice(['html5', 'flex', 'vmrc']),
    help='Client type to generate link.',
    default='flex',
    show_default=True,
)
@pass_context
def compute_vm_get_console(ctx: Configuration, launch, client):
    """Get one-time HTML link to access console."""
    username = ctx.username or click.prompt(
        'Username', default=os.environ.get('VSS_USER', ''), err=True
    )
    password = ctx.password or click.prompt(
        'Password',
        default=os.environ.get('VSS_USER_PASS', ''),
        show_default=False,
        hide_input=True,
        confirmation_prompt=True,
        err=True,
    )
    username = username.decode() if isinstance(username, bytes) else username
    password = password.decode() if isinstance(password, bytes) else password
    auth = (username, password)
    obj = ctx.get_vm_console(ctx.moref, auth=auth, client=client)
    link = obj.get('value')
    # print
    columns = ctx.columns or [('value',)]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # launch
    if launch:
        click.launch(link)


@compute_vm_get.command('consolidate', short_help='Consolidation requirement')
@pass_context
def compute_vm_get_consolidate(ctx):
    """Virtual Machine disk consolidation status."""
    obj = ctx.get_vm_consolidation(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VM_CONSOLIDATION
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.group('controller', invoke_without_command=True)
@pass_context
def compute_vm_get_controllers(ctx: Configuration):
    """Get Controllers (IDE, SCSI, etc)."""
    if click.get_current_context().invoked_subcommand is None:
        obj = ctx.get_vm_controllers(ctx.moref)
        obj = obj or {}
        columns = ctx.columns or const.COLUMNS_VM_CONTROLLERS
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get_controllers.command('scsi', short_help='SCSI adapters')
@click.argument('bus', type=click.INT, required=False)
@click.option('--disks', '-d', help='include disks attached', is_flag=True)
@pass_context
def compute_vm_get_controller_scsi(ctx: Configuration, bus, disks):
    """Virtual machine SCSI controllers and attached disks."""
    if bus is None:
        obj = ctx.get_vm_scsi_devices(ctx.moref)
        columns = ctx.columns or const.COLUMNS_VM_CTRL_MIN
        ctx.echo(format_output(ctx, obj, columns=columns))
    else:
        obj = ctx.get_vm_scsi_device(ctx.moref, bus, disks)
        if disks:
            obj = obj.get('devices', [])
            columns = ctx.columns or const.COLUMNS_VM_CTRL_DISK
            ctx.echo(format_output(ctx, obj, columns=columns))
        else:
            columns = ctx.columns or const.COLUMNS_VM_CTRL
            ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('cpu', short_help='CPU configuration')
@pass_context
def compute_vm_get_cpu(ctx: Configuration):
    """Virtual machine cpu configuration.

    Get CPU count and quick stats.
    """
    columns = ctx.columns or const.COLUMNS_VM_CPU
    obj = ctx.get_vm_cpu(ctx.moref)
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('description', short_help='Description (Metadata)')
@pass_context
def compute_vm_get_description(ctx: Configuration):
    """Virtual machine description. Part of the VSS metadata."""
    obj = ctx.get_vm_vss_description(ctx.moref)
    # print
    columns = ctx.columns or [('value',)]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.group(
    'disk', short_help='Disk configuration', invoke_without_command=True
)
@click.argument('unit', type=click.INT, required=False)
@pass_context
def compute_vm_get_disks(ctx: Configuration, unit):
    """Virtual machine Disk configuration."""
    ctx.unit = unit
    if click.get_current_context().invoked_subcommand is None:
        if ctx.unit:
            obj = ctx.get_vm_disk(ctx.moref, ctx.unit)
            if obj:
                columns = ctx.columns or const.COLUMNS_VM_DISK
                ctx.echo(format_output(ctx, obj, columns=columns, single=True))
            else:
                logging.error('Unit does not exist')
        else:
            objs = ctx.request(f'/vm/{ctx.moref}/disk')
            if objs:
                objs = objs.get('data')
            columns = ctx.columns or const.COLUMNS_VM_DISK_MIN
            ctx.echo(format_output(ctx, objs, columns=columns))


@compute_vm_get_disks.command('backing', short_help='backing info')
@pass_context
def compute_vm_get_disks_backing(ctx: Configuration):
    """Virtual disk backing info."""
    columns = ctx.columns or const.COLUMNS_VM_DISK_BACKING
    obj = ctx.get_vm_disk_backing(ctx.moref, ctx.unit)
    if obj:
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    else:
        logging.error('Disk %s backing could not be found' % ctx.unit)


@compute_vm_get_disks.command('scsi', short_help='scsi controller info')
@pass_context
def compute_vm_get_disks_scsi(ctx: Configuration):
    """Virtual disk SCSI controller info."""
    columns = ctx.columns or const.COLUMNS_VM_DISK_SCSI
    obj = ctx.get_vm_disk_scsi(ctx.moref, ctx.unit)
    if obj:
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    else:
        logging.error('Disk %s SCSI controller could not be found' % ctx.unit)


@compute_vm_get.command('domain', short_help='Running domain')
@pass_context
def compute_vm_get_domain(ctx: Configuration):
    """Virtual machine running domain."""
    obj = ctx.get_vm_domain(ctx.moref)
    columns = ctx.columns or [
        ('MOREF', 'domain.moref'),
        ('NAME', 'domain.name'),
    ]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('event', short_help='Events')
@click.option('-w', '--window', type=int, default=1, help='Time window')
@pass_context
def compute_vm_get_events(ctx: Configuration, window):
    """Get virtual machine related events in given time window."""
    obj = ctx.request(f'/vm/{ctx.moref}/event', params=dict(hours=window))
    obj = obj.get('data')
    columns = ctx.columns or const.COLUMNS_VM_EVENT
    ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('extra-cfg', short_help='GuestInfo extra configs')
@pass_context
def compute_vm_get_extra_config(ctx: Configuration):
    """Get virtual machine guest info via VMware Tools."""
    objs = ctx.get_vm_extra_cfg_options(ctx.moref)
    columns = ctx.columns or const.COLUMNS_EXTRA_CONFIG
    ctx.echo(format_output(ctx, objs, columns=columns))


@compute_vm_get.command('firmware', short_help='Firmware configuration')
@pass_context
def compute_vm_get_firmware(ctx: Configuration):
    """Compute vm get firmware."""
    obj = ctx.get_vm_firmware(ctx.moref)
    columns = ctx.columns or const.COLUMNS_FIRMWARE
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('floppy', short_help='Floppy configuration')
@click.argument('unit', type=int, required=False)
@pass_context
def compute_vm_get_floppies(ctx: Configuration, unit):
    """Virtual machine Floppy configuration."""
    if unit:
        obj = ctx.get_vm_floppy(ctx.moref, unit)
        if obj:
            columns = ctx.columns or const.COLUMNS_VM_CD
            ctx.echo(format_output(ctx, obj, columns=columns, single=True))
        else:
            logging.error('Unit does not exist')
    else:
        devs = ctx.get_vm_floppies(ctx.moref)
        obj = [d.get('data') for d in devs] if devs else []
        columns = ctx.columns or const.COLUMNS_VM_CD_MIN
        ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('folder', short_help='Logical folder')
@pass_context
def compute_vm_get_folder(ctx: Configuration):
    """Virtual machine logical folder."""
    obj = ctx.get_vm_folder(ctx.moref)
    columns = ctx.columns or const.COLUMNS_FOLDER
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('os', short_help='Operating System')
@pass_context
def compute_vm_get_os(ctx: Configuration):
    """Virtual machine Operating system."""
    obj_vm = ctx.get_vm_os(ctx.moref)
    obj_guest = ctx.get_vm_guest_os(ctx.moref)
    obj = {'cfg': obj_vm, 'guest': obj_guest}
    columns = ctx.columns or const.COLUMNS_VM_OS
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    if obj['guest']['guest_id'] is not None:
        vm_os = obj_vm.get('guest_id')
        g_os = obj_guest.get('guest_id')
        status = True if vm_os == g_os else False
        if not status:
            _LOGGING.warning(
                'Operating System does not match '
                'Running Guest OS: {} ≠ {}'.format(vm_os, g_os)
            )


@compute_vm_get.group(
    'guest', short_help='Guest summary', invoke_without_command=True
)
@pass_context
def compute_vm_get_guest(ctx: Configuration):
    """Get virtual machine guest info via VMware Tools."""
    obj = ctx.get_vm_guest(ctx.moref)
    if click.get_current_context().invoked_subcommand is None:
        columns = ctx.columns or const.COLUMNS_VM_GUEST
        ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get_guest.command('os', short_help='Guest OS configuration')
@pass_context
def compute_vm_get_guest_os(ctx: Configuration):
    """Get virtual machine guest OS."""
    obj = ctx.get_vm_guest_os(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VM_GUEST_OS
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get_guest.command(
    'ip', short_help='Guest IP Address configuration'
)
@pass_context
def compute_vm_get_guest_ip(ctx: Configuration):
    """Get virtual machine ip addresses via VMware Tools."""
    obj = ctx.get_vm_guest_ip(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VM_GUEST_IP
    ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('ha-group', short_help='HA Group (Metadata)')
@pass_context
def compute_vm_get_ha_group(ctx: Configuration):
    """Get High Availability Group configuration.

    Part of the VSS metadata.
    """
    obj = ctx.get_vm_vss_ha_group(ctx.moref)
    if obj:
        obj = obj.get('vms', [])
    else:
        obj = []
    columns = ctx.columns or const.COLUMNS_VM_HAGROUP
    ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command(
    'inform', short_help='Informational contacts (Metadata)'
)
@pass_context
def compute_vm_get_inform(ctx: Configuration):
    """Virtual machine informational contacts.

    Part of the VSS metadata.
    """
    obj = ctx.get_vm_vss_inform(ctx.moref)
    if obj:
        obj = dict(inform=obj)
    columns = ctx.columns or [('inform', 'inform.[*]')]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('memory', short_help='Memory configuration')
@pass_context
def compute_vm_get_memory(ctx: Configuration):
    """Virtual machine memory configuration."""
    obj = ctx.get_vm_memory(str(ctx.moref))
    columns = ctx.columns or const.COLUMNS_VM_MEMORY
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('name', short_help='Logical name')
@pass_context
def compute_vm_get_name(ctx: Configuration):
    """Virtual machine human readable name."""
    obj = ctx.get_vm_name(ctx.moref)
    columns = ctx.columns or [('name',)]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('nic', short_help='NIC configuration')
@click.argument('unit', type=int, required=False)
@pass_context
def compute_vm_get_nics(ctx: Configuration, unit):
    """Virtual machine network interface adapters configuration."""
    if unit:
        obj = ctx.get_vm_nic(ctx.moref, unit)
        if obj:
            columns = ctx.columns or const.COLUMNS_VM_NIC
            ctx.echo(format_output(ctx, obj, columns=columns, single=True))
        else:
            logging.error('Unit does not exist')
    else:
        obj = ctx.get_vm_nics(ctx.moref)
        obj = [d.get('data') for d in obj] if obj else []
        columns = ctx.columns or const.COLUMNS_VM_NIC_MIN
        ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('perm', short_help='Permissions')
@click.option(
    '-p', '--page', is_flag=True, help='page results in a less-like format'
)
@pass_context
def compute_vm_get_perms(ctx: Configuration, page):
    """Obtain virtual machine group or user permissions."""
    obj = ctx.get_vm_permission(ctx.moref)
    columns = ctx.columns or const.COLUMNS_OBJ_PERMISSION
    ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command('retire', short_help='Retirement Requests')
@so.filter_opt
@so.sort_opt
@so.all_opt
@so.count_opt
@so.page_opt
@pass_context
def compute_vm_get_retirement(
    ctx: Configuration, filter_by, page, sort, show_all, count
):
    """Virtual Machine retirement requests."""
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE
    params = dict(expand=1, sort='created_on,desc')
    if all(filter_by):
        params['filter'] = ';'.join(filter_by)
    if all(sort):
        params['sort'] = ';'.join(sort)
    # make request
    with ctx.spinner(disable=ctx.debug):
        _requests = ctx.get_vm_retirement_requests(
            ctx.moref, show_all=show_all, per_page=count, **params
        )

    output = format_output(ctx, _requests, columns=columns)
    # page results
    if page:
        click.echo_via_pager(output)
    else:
        ctx.echo(output)


@compute_vm_get.command('snapshot', short_help='Snapshots')
@click.argument('snapshot_id', type=int, required=False)
@pass_context
def compute_vm_get_snapshot(ctx: Configuration, snapshot_id):
    """Virtual Machine snapshots."""
    if snapshot_id:
        obj = ctx.get_vm_snapshot(ctx.moref, snapshot_id)
        columns = ctx.columns or const.COLUMNS_VM_SNAP
        ctx.echo(format_output(ctx, obj, columns=columns, single=True))
    else:
        obj = ctx.get_vm_snapshots(ctx.moref)
        columns = ctx.columns or const.COLUMNS_VM_SNAP_MIN
        ctx.echo(format_output(ctx, obj, columns=columns))


@compute_vm_get.command(
    'spec-api',
    short_help='Cloud API configuration specification',
    context_settings={"ignore_unknown_options": True},
)
@click.argument('spec_file', type=click.Path(), required=False)
@click.option(
    '-e', '--edit', is_flag=True, required=False, help='Edit before writing'
)
@pass_context
def compute_vm_get_spec_api(ctx: Configuration, spec_file, edit):
    """Cloud API  Virtual machine configuration specification."""
    if ctx.output in ['auto', 'table']:
        _LOGGING.warning(f'Input set to {ctx.output}. Falling back to yaml')
        ctx.output = 'yaml'
    f_name = spec_file or f'{ctx.moref}-api-spec.{ctx.output}'
    # get obj
    obj = ctx.get_vm_spec(ctx.moref)
    new_raw = None
    if edit:
        obj_raw = raw_format_output(
            ctx.output, obj, ctx.yaml(), highlighted=False
        )
        new_raw = click.edit(obj_raw, extension=f'.{ctx.output}')

    if ctx.output == 'json':
        import json

        if new_raw:
            obj = json.loads(new_raw)
        with open(f_name, 'w') as fp:
            json.dump(obj, fp=fp, indent=2, sort_keys=False)
    else:
        if new_raw:
            obj = ctx.yaml_load(new_raw)
        with open(f_name, 'w') as fp:
            ctx.yaml_dump_stream(obj, stream=fp)
    ctx.echo(f'Written to {f_name}')


@compute_vm_get.command(
    'spec',
    short_help='CLI configuration specification',
    context_settings={"ignore_unknown_options": True},
)
@click.argument('spec_file', type=click.Path(), required=False)
@click.option(
    '-e', '--edit', is_flag=True, required=False, help='Edit before writing'
)
@pass_context
def compute_vm_get_spec(ctx: Configuration, spec_file, edit):
    """CLI Virtual machine configuration specification."""
    if ctx.output in ['auto', 'table']:
        _LOGGING.warning(f'Input set to {ctx.output}. Falling back to yaml')
        ctx.output = 'yaml'
    f_name = spec_file or f'{ctx.moref}-cli-spec.{ctx.output}'
    # get obj
    obj = ctx.get_vm_spec(ctx.moref)
    file_spec = os.path.join(const.DEFAULT_DATA_PATH, 'shell.yaml')
    # proceed to load file
    with open(file_spec) as data_file:
        raw = data_file.read()
    template = ctx.yaml_load(raw)
    # obj rewritten with cli spec
    obj = ctx.get_cli_spec_from_api_spec(payload=obj, template=template)
    new_raw = None
    if edit:
        obj_raw = raw_format_output(
            ctx.output, obj, ctx.yaml(), highlighted=False
        )
        new_raw = click.edit(obj_raw, extension=f'.{ctx.output}')

    if ctx.output == 'json':
        import json

        if new_raw:
            obj = json.loads(new_raw)
        with open(f_name, 'w') as fp:
            json.dump(obj, fp=fp, indent=2, sort_keys=False)
    else:
        if new_raw:
            obj = ctx.yaml_load(new_raw)
        with open(f_name, 'w') as fp:
            ctx.yaml_dump_stream(obj, stream=fp)
    ctx.echo(f'Written to {f_name}')


@compute_vm_get.command('state', short_help='Power state')
@pass_context
def compute_vm_get_state(ctx: Configuration):
    """Virtual machine running and power state."""
    obj = ctx.get_vm_state(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VM_STATE
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('stats', short_help='Performance statistics')
@click.argument('kind', type=click.Choice(['memory', 'io', 'cpu', 'net']))
@pass_context
def compute_vm_get_stats(ctx: Configuration, kind):
    """Get virtual machine memory, io, cpu and network performance statistics.

    Choose between: io, memory, cpu or net. For example:

    vss-cli compute vm get <name-or-vm_id> stats memory
    """
    lookup = {
        'cpu': ctx.get_vm_performance_cpu,
        'memory': ctx.get_vm_performance_memory,
        'io': ctx.get_vm_performance_io,
        'net': ctx.get_vm_performance_net,
    }

    if not ctx.is_powered_on_vm(ctx.moref):
        raise VssCliError('Cannot perform operation in current power state')
    obj = lookup[kind](ctx.moref)
    columns = ctx.columns or [(i,) for i in obj.keys()]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('template', short_help='Template configuration')
@pass_context
def compute_vm_get_template(ctx: Configuration):
    """Virtual machine template state."""
    obj = ctx.is_vm_template(ctx.moref)
    columns = ctx.columns or [('is_template',)]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('tools', short_help='VMware Tools Status')
@pass_context
def compute_vm_get_tools(ctx: Configuration):
    """Virtual machine VMware Tools status."""
    obj = ctx.get_vm_tools(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VM_TOOLS
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('usage', short_help='Usage (Metadata)')
@pass_context
def compute_vm_get_usage(ctx: Configuration):
    """Get current virtual machine usage.

    Part of the VSS metadata and the name prefix (YYMMP-) is composed
    by the virtual machine usage, which is intended to specify
    whether it will be hosting a Production, Development,
    QA, or Testing system.
    """
    obj = ctx.get_vm_vss_usage(ctx.moref)
    columns = ctx.columns or [('usage', 'value')]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('version', short_help='Hardware (VMX) version')
@pass_context
def compute_vm_get_version(ctx: Configuration):
    """Get VMX hardware version."""
    obj = ctx.get_vm_version(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VM_HW
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command(
    'vmrc-copy-paste', short_help='Get VMRC copy/paste settings status'
)
@click.option(
    '-o', '--options', is_flag=True, required=False, help='Include options'
)
@pass_context
def compute_vm_get_vmrc_copy_paste(ctx: Configuration, options):
    """Get VMRC Copy-Paste settings."""
    obj = ctx.get_vm_vmrc_copy_paste(ctx.moref, options=options)
    columns = ctx.columns or const.COLUMNS_VMRC
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('vss-option', short_help='Get VSS Option status')
@pass_context
def compute_vm_get_vss_option(ctx: Configuration):
    """Get VSS Option status."""
    obj = ctx.get_vm_vss_options(ctx.moref)
    columns = ctx.columns or const.COLUMNS_VSS_OPTIONS
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('vss-service', short_help='Get VSS Service')
@pass_context
def compute_vm_get_vss_service(ctx: Configuration):
    """Get VSS Service configuration."""
    obj = ctx.get_vm_vss_service(ctx.moref)
    columns = ctx.columns  # or const.COLUMNS_VSS_SERVICE
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))


@compute_vm_get.command('vsphere-link', short_help='Get vSphere link to VM')
@click.option(
    '-l', '--launch', is_flag=True, help='Launch link to default handler'
)
@pass_context
def compute_vm_get_vsphere_link(ctx: Configuration, launch: bool):
    """Get vSphere Client Link to VM."""
    obj = ctx.get_vm_vsphere_link(ctx.moref)
    link = obj.get('value')
    # print
    columns = ctx.columns or [('value',)]
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # launch
    if launch:
        click.launch(link)


@compute_vm.group(
    'set',
    short_help='Set virtual machine attribute',
    invoke_without_command=True,
)
@click.argument(
    'vm_id_or_name',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.virtual_machines,
)
@click.option(
    '-s',
    '--schedule',
    type=click.DateTime(formats=const.SUPPORTED_DATETIME_FORMATS),
    required=False,
    default=None,
    help='Schedule change in a given point in time based'
    ' on format YYYY-MM-DD HH:MM.',
)
@click.option(
    '-u',
    '--user-meta',
    help='User metadata in key=value format. '
    'These tags are stored in the request.',
    required=False,
    default=None,
)
@so.dry_run_opt
@pass_context
def compute_vm_set(
    ctx: Configuration,
    vm_id_or_name: str,
    schedule,
    user_meta: str,
    dry_run: bool,
):
    """Manage virtual machine resources.

    Such as cpu, memory, disk, network backing, cd, etc.
    """
    # setup payload opts
    ctx.user_meta = dict(to_tuples(user_meta))
    ctx.schedule = schedule
    # whether to wait for requests
    # check for vm
    _vm = ctx.get_vm_by_id_or_name(vm_id_or_name)
    ctx.moref = _vm[0]['moref']
    # set additional props
    if user_meta:
        ctx.payload_options['user_meta'] = ctx.user_meta
    if schedule:
        ctx.payload_options['schedule'] = ctx.schedule.strftime(
            const.DEFAULT_DATETIME_FMT
        )
    # set dry run and output to json
    ctx.set_dry_run(dry_run)
    if click.get_current_context().invoked_subcommand is None:
        raise click.UsageError('Sub command is required')


@compute_vm_set.command('admin', short_help='Administrator')
@click.argument('name', type=click.STRING, required=True)
@click.argument(
    'email', type=click.STRING, required=True, callback=validate_email
)
@click.argument(
    'phone', type=click.STRING, required=True, callback=validate_phone_number
)
@pass_context
def compute_vm_set_admin(ctx: Configuration, name, email, phone):
    """Set or update virtual machine administrator in metadata.

    vss-cli compute vm set <name-or-vm_id> admin "Admin Name"
    admin.email@utoronto.ca 416-666-6666
    """
    payload = dict(name=name, phone=phone, email=email, vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # process request
    obj = ctx.update_vm_vss_admin(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('alarm', short_help='Acknowledge or clear alarms')
@click.argument('alarm_moref', type=click.STRING, required=True)
@click.option(
    '-a',
    '--action',
    type=click.Choice(['ack', 'cl']),
    help='Action to perform',
    required=True,
)
@pass_context
def compute_vm_set_alarm(ctx: Configuration, action, alarm_moref):
    """Acknowledge or clear a given alarm.

    Obtain alarm moref by:

    vss-cli compute vm get <name-or-vm_id> alarm

    vss-cli compute vm set <name-or-vm_id> alarm <moref> --action ack

    """
    payload = dict(vm_id=ctx.moref, moref=alarm_moref)
    # add common options
    payload.update(ctx.payload_options)
    # action
    if action == 'ack':
        obj = ctx.ack_vm_alarm(**payload)
    else:
        obj = ctx.clear_vm_alarm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'boot-bios', short_help='Enable or disable Boot to BIOS'
)
@click.option(
    '--on/--off',
    is_flag=True,
    help='Enable/Disable boot to BIOS',
    default=False,
)
@pass_context
def compute_vm_set_boot_bios(ctx: Configuration, on):
    """Update virtual machine boot configuration to boot directly to BIOS.

    vss-cli compute vm set <name-or-vm_id> boot-bios --on
    vss-cli compute vm set <name-or-vm_id> boot-bios --off
    """
    payload = dict(vm_id=ctx.moref, boot_bios=on)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_boot_bios(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('boot-delay', short_help='Boot delay in milliseconds')
@click.argument('delay-in-ms', type=click.INT, required=True)
@pass_context
def compute_vm_set_boot_delay(ctx: Configuration, delay_in_ms):
    """Update virtual machine boot delay time (ms).

    vss-cli compute vm set <name-or-vm_id> boot-delay 5000
    """
    payload = dict(vm_id=ctx.moref, boot_delay_ms=delay_in_ms)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_boot_delay(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('cd', short_help='CD/DVD device management')
@pass_context
def compute_vm_set_cd(ctx: Configuration):
    """Manage virtual CD/DVD devices.

    Add and update CD/DVD backing.
    """
    pass


@compute_vm_set_cd.command('mk', short_help='Create CD/DVD unit')
@click.option(
    '-b',
    '--backing',
    type=click.STRING,
    required=True,
    multiple=True,
    help='Update CD/DVD backing device to given ISO path or Client device.',
    shell_complete=autocompletion.isos,
)
@pass_context
def compute_vm_set_cd_mk(ctx: Configuration, backing):
    """Create virtual machine CD/DVD unit with ISO or client backing.

    vss-cli compute vm set <name-or-vm_id> cd mk --backing <name-or-path-or-id>

    vss-cli compute vm set <name-or-vm_id> cd mk --backing client
    """
    p_backing = []
    for b in backing:
        # get iso reference
        iso_ref = ctx.get_iso_by_name_or_path(b)
        _LOGGING.debug(f'Will create {iso_ref}')
        p_backing.append(str(iso_ref[0]['id']))
    # generate payload
    payload = dict(vm_id=ctx.moref, backings=p_backing)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_cd(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_cd.command('up', short_help='Update CD/DVD unit')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-b',
    '--backing',
    type=click.STRING,
    required=True,
    help='Update CD/DVD backing device ' 'to given ISO path or Client device.',
    shell_complete=autocompletion.isos,
)
@pass_context
def compute_vm_set_cd_up(ctx: Configuration, unit, backing):
    """Update virtual machine CD/DVD backend to ISO or client.

    vss-cli compute vm set <name-or-vm_id> cd up <unit> -b <name-or-path-or-id>

    vss-cli compute vm set <name-or-vm_id> cd up <unit> -b client
    """
    # get iso reference
    iso_ref = ctx.get_iso_by_name_or_path(backing)
    _LOGGING.debug(f'Will mount {iso_ref}')
    # generate payload
    payload = dict(vm_id=ctx.moref, unit=unit, iso=iso_ref[0]['path'])
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_cd(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('client', short_help='Client (Metadata)')
@click.argument('client', type=click.STRING, required=True)
@pass_context
def compute_vm_set_client(ctx: Configuration, client):
    """Update virtual machine client department.

    vss-cli compute vm set <name-or-vm_id> client <New-Client>
    """
    # generate payload
    payload = dict(vm_id=ctx.moref, client=client)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_client(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('client-note', short_help='Client note (Metadata)')
@click.argument('notes', required=True)
@click.option(
    '--replace',
    '-r',
    is_flag=True,
    required=False,
    help="Whether to replace existing value.",
)
@pass_context
def compute_vm_set_client_note(ctx: Configuration, notes, replace):
    """Set or update virtual machine client notes in metadata.

    vss-cli compute vm set <name-or-vm_id> client-note 'New note'
    """
    if not replace:
        _old_notes = ctx.get_vm_notes(ctx.moref)
        old_notes = _old_notes.get('value') or ""
        notes = f"{old_notes}\n{notes}"
    # generate payload
    payload = dict(vm_id=ctx.moref, notes=notes)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_notes(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('consolidate', short_help='Disk consolidation')
@pass_context
def compute_vm_set_consolidate(ctx: Configuration):
    """Perform virtual machine disk consolidation.

    vss-cli compute vm set --schedule <timestamp> <name-or-vm_id> consolidate
    """
    # generate payload
    payload = dict(vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.consolidate_vm_disks(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('cpu')
@pass_context
def compute_vm_set_cpu(ctx: Configuration):
    """Update virtual machine CPU count and settings."""
    pass


@compute_vm_set_cpu.command(
    'count', short_help='Update CPU count and cores per socket.'
)
@c_so.cpu_cps_opt
@click.argument('cpu_count', type=click.INT, required=True)
@pass_context
def compute_vm_set_cpu_count(
    ctx: Configuration, cpu_count: int, cores_per_socket: Optional[int] = 1
):
    """Update CPU count and cores per socket.

    Note: Refer to Setting the number of cores per
    CPU (https://kb.vmware.com/s/article/1010184) when setting
    cores per socket.
    """
    # generate payload
    payload = dict(
        vm_id=ctx.moref, number=cpu_count, cores_per_socket=cores_per_socket
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.set_vm_cpu(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_cpu.command('hot-add', short_help='Enable/disable CPU hot add')
@click.argument('status', type=click.Choice(['on', 'off']), required=True)
@pass_context
def compute_vm_set_cpu_hot_add(ctx: Configuration, status):
    """Update CPU hot add settings."""
    lookup = {'on': True, 'off': False}
    payload = dict(vm_id=ctx.moref, hot_add=lookup[status])
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_cpu_hot_add(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('custom-spec', short_help='Custom specification')
@click.option(
    '--hostname', '-h', type=click.STRING, required=True, help='OS hostname.'
)
@click.option(
    '--domain', '-m', type=click.STRING, required=True, help='OS domain.'
)
@click.option(
    '--dns',
    '-n',
    type=click.STRING,
    multiple=True,
    required=False,
    help='DNS servers list.',
)
@click.option(
    '--interface',
    '-i',
    type=click.STRING,
    required=False,
    multiple=True,
    help='Interfaces to customize in json format.',
)
@click.option(
    '--dns-suffix',
    '-s',
    type=click.STRING,
    multiple=True,
    required=False,
    help='list of DNS search domains to add to the DNS configuration.',
)
@pass_context
def compute_vm_set_custom_spec(
    ctx: Configuration, hostname, domain, dns, interface, dns_suffix
):
    """Set up Guest OS customization specification.

    Virtual machine power state require is powered off.
    """
    if ctx.is_powered_on_vm(ctx.moref):
        raise Exception(
            'Cannot perform operation on VM with current power state'
        )
    # temp custom_spec
    _custom_spec = dict(hostname=hostname, domain=domain)
    if dns:
        _custom_spec['dns'] = dns
    if dns_suffix:
        _custom_spec['dns_suffix'] = dns_suffix
    interfaces = list()
    # interfaces
    if interface:
        import json

        for iface in interface:
            validate_json_type(ctx, '', iface)
            _if = json.loads(iface)
            interfaces.append(ctx.get_custom_spec_interface(**_if))
    else:
        _LOGGING.warning('No interfaces were received from input')
    # update custom spec with interfaces
    _custom_spec.update({'interfaces': interfaces})
    # create custom_spec
    custom_spec = ctx.get_custom_spec(**_custom_spec)
    # create payload
    payload = dict(vm_id=ctx.moref, custom_spec=custom_spec)
    # add common options
    payload.update(ctx.payload_options)
    # process request
    # submit custom_spec
    obj = ctx.create_vm_custom_spec(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group(
    'extra-cfg', short_help='GuestInfo extra config entries.'
)
@pass_context
def compute_vm_set_extra_config(ctx: Configuration):
    """Manage VMware **guestinfo** interface options.

    Available to the VM guest operating system via VMware Tools:

    vmtoolsd --cmd "info-get guestinfo.<option>"
    """
    pass


@compute_vm_set_extra_config.command(
    'mk', short_help='Create guestInfo extra config entries.'
)
@c_sa.extra_config_arg
@pass_context
def compute_vm_set_extra_config_mk(ctx: Configuration, key_value):
    """Create **guestinfo** interface extra configuration options.

    vss-cli compute vm set <name-or-vm_id> extra-cfg mk key1=value2 key2=value2
    """
    # process input
    # assemble payload
    payload = dict(vm_id=ctx.moref, options=key_value)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_extra_cfg_options(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_extra_config.command(
    'up', short_help='Update guestInfo extra config entries.'
)
@c_sa.extra_config_arg
@pass_context
def compute_vm_set_extra_config_up(ctx: Configuration, key_value):
    """Update **guestinfo** interface extra configuration options.

    vss-cli compute vm set <name-or-vm_id> extra-cfg up key1=value2 key2=value2
    """
    # assemble payload
    payload = dict(vm_id=ctx.moref, options=key_value)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_extra_cfg_options(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_extra_config.command(
    'rm', short_help='Remove guestInfo extra config option keys.'
)
@click.argument('key', type=click.STRING, required=True, nargs=-1)
@pass_context
def compute_vm_set_extra_config_rm(ctx: Configuration, key):
    """Remove **guestinfo** interface extra configuration options.

    vss-cli compute vm set <name-or-vm_id> extra-cfg rm key1 key2 keyN
    """
    # assemble payload
    payload = dict(vm_id=ctx.moref, options=key)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.delete_vm_extra_cfg_options(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('description', short_help='Description (Metadata)')
@click.argument('description', required=True)
@pass_context
def compute_vm_set_description(ctx: Configuration, description):
    """Set or update virtual machine description in metadata.

    vss-cli compute vm set <name-or-vm_id> description 'new description'
    """
    payload = dict(vm_id=ctx.moref, description=description)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_description(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('disk', short_help='Disk management')
@pass_context
def compute_vm_set_disk(ctx: Configuration):
    """Manage virtual machine disks.

    Add, expand and remove virtual disks.
    """
    pass


@compute_vm_set_disk.command('mk', short_help='Create disk(s)')
@c_so.disk_opt
@pass_context
def compute_vm_set_disk_mk(ctx: Configuration, disk):
    """Create virtual machine disk.

    vss-cli compute vm set <name-or-vm_id> disk mk
    -i <capacity>=<backing_mode>=<backing_sharing>=<backing_file>

    vss-cli compute vm set <name-or-vm_id> disk mk -i 10 -i 40

    vss-cli compute vm set <name-or-vm_id> disk mk -i 10
    -i 100=independent_persistent
    """
    payload = dict(vm_id=ctx.moref, disks=disk)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_disk(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_disk.command('up', short_help='Update disk settings')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-c',
    '--capacity',
    type=click.INT,
    required=False,
    help='Update disk capacity in GB.',
)
@click.option(
    '-s',
    '--scsi',
    type=click.INT,
    required=False,
    help='Update disk SCSI adapter',
)
@click.option(
    '-m',
    '--backing-mode',
    shell_complete=autocompletion.vm_disk_backing_modes,
    help='Update disk backing mode default [persistent]',
)
@click.option(
    '-r',
    '--sharing',
    shell_complete=autocompletion.vm_disk_sharing,
    help='Update disk sharing mode default [sharingnone]',
)
@click.option(
    '-n',
    '--notes',
    type=click.STRING,
    required=False,
    help='Update disk capacity notes.',
)
@pass_context
def compute_vm_set_disk_up(
    ctx: Configuration, unit, capacity, scsi, backing_mode, sharing, notes
):
    """Update virtual machine disk capacity.

    vss-cli compute vm set <name-or-vm_id> disk up --capacity 30 <unit>

    vss-cli compute vm set <name-or-vm_id> disk up --scsi=<bus> <unit>

    vss-cli compute vm set <name-or-vm_id> disk up
    --backing-mode=independent_persistent <unit>

    vss-cli compute vm set <name-or-vm_id> disk up --sharing=<mode> <unit>
    """
    payload = dict(vm_id=ctx.moref, unit=unit)
    # add common options
    payload.update(ctx.payload_options)
    if capacity:
        payload['value_gb'] = capacity
        # request
        obj = ctx.update_vm_disk_capacity(**payload)
    elif scsi is not None:
        payload['bus_number'] = scsi
        obj = ctx.update_vm_disk_scsi(**payload)
    elif backing_mode is not None:
        payload['mode'] = backing_mode
        obj = ctx.update_vm_disk_backing_mode(**payload)
    elif sharing is not None:
        payload['sharing'] = sharing
        obj = ctx.update_vm_disk_backing_sharing(**payload)
    elif notes is not None:
        payload['notes'] = notes
        c_notes = ctx.get_vm_disk_notes(ctx.moref, unit)
        if c_notes.get('notes'):
            ctx.echo(f"Existing notes found: \t{c_notes.get('notes')}")
            replace = click.confirm('Would you like to replace?')
            payload['append'] = not replace
        obj = ctx.update_vm_disk_notes(**payload)
        ctx.echo(
            format_output(
                ctx, [obj], columns=[('label',), ('notes',)], single=True
            )
        )
        return
    else:
        raise click.BadOptionUsage(
            '',
            'Either -c/--capacity or -s/--scsi '
            'or -m/--backing-mode or -r/--sharing is required.',
        )
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_disk.command('rm', short_help='Remove disk from vm')
@click.argument('unit', type=click.INT, required=True, nargs=-1)
@click.option(
    '-r', '--rm', is_flag=True, default=False, help='Confirm disk removal'
)
@pass_context
def compute_vm_set_disk_rm(ctx: Configuration, unit, rm):
    """Remove virtual machine disks.

    vss-cli compute vm set <name-or-vm_id> disk rm <unit> <unit> ...

    Warning: data will be lost.
    """
    payload = dict(vm_id=ctx.moref, units=list(unit))
    # add common options
    payload.update(ctx.payload_options)
    # confirm
    confirm = rm or click.confirm(
        f'Are you sure you want to delete disk unit {unit}?'
    )
    if confirm:
        obj = ctx.delete_vm_disks(**payload)
    else:
        raise click.ClickException('Cancelled by user.')
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('domain', short_help='Domain migration')
@click.argument(
    'name_or_moref',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.domains,
)
@click.option(
    '-f',
    '--force',
    is_flag=True,
    help='Shut down or power off before migration.',
)
@click.option('-o', '--on', is_flag=True, help='Power of after migrating')
@pass_context
def compute_vm_set_domain(ctx: Configuration, name_or_moref, force, on):
    """Migrate a virtual machine to another fault domain.

    In order to proceed with the virtual machine relocation,
    in some cases the VM is required to be in a powered off state.

    The `force` flag will send a shutdown signal anf if times out,
    will perform a power off task. After migration completes, the `on` flag
    indicates to power on the virtual machine.

    vss-cli compute vm set <name-or-vm_id> domain <name-or-moref> --force --on
    """
    _domain = ctx.get_domain_by_name_or_moref(name_or_moref)
    if not _domain:
        raise click.BadArgumentUsage(f'Domain {_domain} does not exist')
    domain_moref = _domain[0]['moref']
    payload = dict(
        vm_id=ctx.moref, moref=domain_moref, poweron=on, force=force
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_domain(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('export', short_help='Export to OVF')
@pass_context
def compute_vm_set_export(ctx: Configuration):
    """Export current virtual machine to OVF.

    vss-cli compute vm set <name-or-vm_id> export
    """
    payload = dict(vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.export_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('firmware', short_help='Update firmware')
@c_sa.firmware_arg
@pass_context
def compute_vm_set_firmware(ctx: Configuration, firmware):
    """Update current vm firmware."""
    payload = dict(vm_id=ctx.moref, firmware=firmware)
    obj = ctx.update_vm_firmware(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('floppy', short_help='Floppy backing')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-i',
    '--image',
    type=click.STRING,
    required=False,
    default='client',
    help='Update floppy backing device to given flp image path.',
    shell_complete=autocompletion.floppies,
)
@pass_context
def compute_vm_set_floppy(ctx: Configuration, unit, image):
    """Update virtual machine floppy backend to Image or client."""
    img_ref = ctx.get_floppy_by_name_or_path(image)
    _LOGGING.debug(f'Will mount {img_ref}')
    image = img_ref[0].get('path')
    # generate payload
    payload = dict(vm_id=ctx.moref, unit=unit, image=image)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_floppy(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('folder', short_help='Logical folder')
@click.argument(
    'name-moref-path',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.folders,
)
@pass_context
def compute_vm_set_folder(ctx: Configuration, name_moref_path):
    """Move vm from logical folder."""
    # create payload
    payload = dict(vm_id=ctx.moref)
    # lookup for folder
    _folder = ctx.get_folder_by_name_or_moref_path(name_moref_path)
    payload['folder_moId'] = _folder[0]['moref']
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_folder(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('guest-cmd', short_help='Execute command on OS host')
@click.option(
    '-u',
    '--username',
    help='Guest Operating System username or via '
    'environment variable VSS_CMD_USER',
    envvar='VSS_CMD_USER',
)
@click.option(
    '-p',
    '--password',
    help='Guest Operating System username password or via '
    'environment variable VSS_CMD_USER_PASS',
    envvar='VSS_CMD_USER_PASS',
)
@click.option(
    '-e',
    '--env',
    multiple=True,
    help='Environment variables in KEY=value format.',
)
@click.argument('cmd', type=click.STRING, required=True)
@click.argument('cmd-args', type=click.STRING, required=True)
@pass_context
def compute_vm_set_guest_cmd(ctx, cmd, cmd_args, env, username, password):
    """Execute a command in the Guest Operating system.

    vss-cli compute vm set <name-or-vm_id> guest-cmd "/bin/echo"
    "Hello > /tmp/hello.txt"

    Note: VMware Tools must be installed and running.
    """
    username = username or click.prompt('Username', err=True)
    password = password or click.prompt(
        'Password',
        show_default=False,
        hide_input=True,
        confirmation_prompt=True,
        err=True,
    )
    # check vmware tools status
    vmt = ctx.get_vm_tools(ctx.moref)
    if not vmt:
        raise click.BadParameter(
            f'VMware Tools status could not be checked on {ctx.moref} '
        )
    if vmt.get('running_status') not in ["guestToolsRunning"]:
        raise click.BadParameter(
            f'VMware Tools must be running ' f'on {ctx.moref} to execute cmd.'
        )
    # creating payload
    payload = dict(
        vm_id=ctx.moref,
        user=username,
        pwd=password,
        cmd=cmd,
        arg=cmd_args,
    )
    if env:
        payload['env'] = env
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.run_cmd_guest_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('os', short_help='Update operating system')
@click.argument(
    'guest-id',
    type=click.STRING,
    required=True,
    shell_complete=autocompletion.operating_systems,
)
@pass_context
def compute_vm_set_guest_os(ctx: Configuration, guest_id):
    """Update operating system configuration.

    vss-cli compute vm set <name-or-vm_id> os <name-or-id>
    """
    g_os = ctx.get_os_by_name_or_guest(guest_id)
    g_id = g_os[0]['guest_id']
    # create payload
    payload = dict(vm_id=ctx.moref, os=g_id)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_os(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('ha-group', short_help='HA Group (Metadata)')
@pass_context
def compute_vm_set_ha_group(ctx: Configuration):
    """Manage HA group by tagging virtual machines.

    Checks will run every 3 hours to validate virtual machine
    association and domain separation.
    """
    pass


@compute_vm_set_ha_group.command('rm', short_help='Remove VM from HA-Group')
@pass_context
def compute_vm_set_ha_group_rm(ctx: Configuration):
    """Remove given VM from HA-Group.

    vss-cli compute vm set <name-or-vm_id> ha-group rm
    """
    # request
    obj = ctx.delete_vm_vss_ha_group(vm_id=ctx.moref)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_ha_group.command('mg', short_help='Migrate VM HA-Group')
@pass_context
def compute_vm_set_ha_group_mg(ctx: Configuration):
    """Remove given VM from HA-Group.

    vss-cli compute vm set <name-or-vm_id> ha-group mg
    """
    # request
    obj = ctx.migrate_vm_vss_ha_group(vm_id=ctx.moref)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_ha_group.command(
    'mk', short_help='Create HA-Group with multiple VMs'
)
@click.argument('vm_id', type=click.STRING, nargs=-1, required=True)
@click.option(
    '-r',
    '--replace',
    is_flag=True,
    required=False,
    help='Replace existing value.',
)
@pass_context
def compute_vm_set_ha_group_mk(ctx: Configuration, vm_id, replace):
    """Create HA Group by tagging VMs together.

    vss-cli compute vm set <name-or-vm_id> ha-group mk -r <vm_id-1> <vm_id-n>
    """
    valid_vms = list()
    for vm in vm_id:
        _vm = ctx.get_vm_by_id_or_name(vm, silent=True)
        if not _vm:
            _LOGGING.warning(f'{vm} could not be found')
        else:
            valid_vms.append(_vm[0])

    if len(valid_vms) < len(vm_id):
        if not click.confirm(
            f'Found {len(valid_vms)} but provided {len(vm_id)} vms. '
            f'Would you like to continue?'
        ):
            raise click.Abort('Cancelled by user.')

    # create payload
    payload = dict(
        append=not replace,
        vms=list(map(lambda x: x['moref'], valid_vms)),
        vm_id=str(ctx.moref),
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_ha_group(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'inform', short_help='Informational contacts (Metadata)'
)
@click.argument(
    'email',
    type=click.STRING,
    nargs=-1,
    required=True,
    callback=flexible_email_args,
)
@click.option(
    '-r',
    '--replace',
    is_flag=True,
    required=False,
    help='Replace existing value.',
)
@pass_context
def compute_vm_set_inform(ctx: Configuration, email, replace):
    """Update or set informational contacts emails in metadata.

    vss-cli compute vm set <name-or-vm_id> inform <email-1> <email-n>
    """
    for e in email:
        validate_email(ctx, '', e)
    # create payload
    payload = dict(append=not replace, emails=list(email), vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_inform(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('memory')
@pass_context
def compute_vm_set_memory(ctx: Configuration):
    """Update virtual machine Memory count and settings."""
    pass


@compute_vm_set_memory.command('size', short_help='Update memory size in GB')
@click.argument('memory_gb', type=click.INT, required=True)
@pass_context
def compute_vm_set_memory_size(ctx: Configuration, memory_gb):
    """Update virtual machine memory size in GB.

    vss-cli compute vm set <name-or-vm_id> memory size <memory_gb>
    """
    # create payload
    payload = dict(sizeGB=memory_gb, vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.set_vm_memory(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_memory.command(
    'hot-add', short_help='Enable/disable Memory hot add'
)
@click.argument('status', type=click.Choice(['on', 'off']), required=True)
@pass_context
def compute_vm_set_memory_hot_add(ctx: Configuration, status):
    """Enable or disable virtual machine memory hot-add setting.

    vss-cli compute vm set <name-or-vm_id> memory hot-add on|off

    """
    lookup = {'on': True, 'off': False}
    # create payload
    payload = dict(vm_id=ctx.moref, hot_add=lookup[status])
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_memory_hot_add(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('name', short_help='Logical name')
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_vm_set_name(ctx: Configuration, name):
    """Update virtual machine name only.

    vss-cli compute vm set <name-or-vm_id> name <new-name>

    Note. It does not update VSS prefix YYMM{P|D|Q|T}.
    """
    payload = dict(name=name, vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.rename_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('nic', short_help='Network adapter management')
@pass_context
def compute_vm_set_nic(ctx: Configuration):
    """Add, remove or update virtual machine network adapters."""
    pass


@compute_vm_set_nic.command('up', short_help='Update NIC unit')
@click.argument('unit', type=click.INT, required=True)
@click.option(
    '-n',
    '--network',
    type=click.STRING,
    help='Virtual network moref',
    shell_complete=autocompletion.networks,
)
@click.option(
    '-s',
    '--state',
    type=click.Choice(['connect', 'disconnect']),
    help='Updates nic state',
)
@click.option(
    '-a',
    '--adapter',
    type=click.STRING,
    help='Updates nic adapter type',
    shell_complete=autocompletion.virtual_nic_types,
)
@pass_context
def compute_vm_set_nic_up(ctx: Configuration, unit, network, state, adapter):
    """Update network adapter backing network, type or state.

    vss-cli compute vm set <name-or-vm_id> nic up <unit> --adapter <type>

    vss-cli compute vm set <name-or-vm_id> nic up <unit> --network <network>
    """
    # create payload
    payload = dict(vm_id=ctx.moref, nic=unit)
    # add common options
    payload.update(ctx.payload_options)
    # process request
    lookup = {
        'network': ctx.update_vm_nic_network,
        'state': ctx.update_vm_nic_state,
        'type': ctx.update_vm_nic_type,
    }
    # select attr
    if network:
        # search by name or moref
        net = ctx.get_network_by_name_or_moref(network)
        attr = 'network'
        value = net[0]['moref']
    elif state:
        attr = 'state'
        value = state
    elif adapter:
        n_type = ctx.get_vm_nic_type_by_name(adapter)
        attr = 'type'
        value = n_type[0]['type']
    else:
        raise click.UsageError('Select at least one setting to change')
    _LOGGING.debug(f'Update NIC {unit} {attr} to {value}')
    # lookup function to call
    f = lookup[attr]
    payload[attr] = value
    # request
    obj = f(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_nic.command('mk', short_help='Create NIC unit')
@c_so.networks_opt
@pass_context
def compute_vm_set_nic_mk(ctx: Configuration, net):
    """Add network adapter specifying backing network and adapter type.

    vss-cli compute vm set <name-or-vm_id> nic mk
    -n <moref-or-name>=<nic-type> -n <moref-or-name>
    """
    # create payload
    payload = dict(vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # payload
    payload['networks'] = net
    # request
    obj = ctx.create_vm_nic(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_nic.command('rm', short_help='Remove NIC unit')
@click.argument('unit', type=click.INT, required=True, nargs=-1)
@click.option(
    '-c', '--confirm', is_flag=True, default=False, help='Confirm nic removal'
)
@pass_context
def compute_vm_set_nic_rm(ctx: Configuration, unit, confirm):
    """Remove given network adapters.

    vss-cli compute vm set <name-or-vm_id> nic rm <unit> <unit> ...
    """
    # create payload
    payload = dict(vm_id=ctx.moref)
    units_payload = []
    # add common options
    payload.update(ctx.payload_options)
    confirm_message = list()
    # validate adapters
    for n in unit:
        _nic = ctx.get_vm_nic(vm_id=ctx.moref, nic=n)
        if _nic:
            _nic = _nic.pop()
            _message = const.DEFAULT_NIC_DEL_MSG.format(**_nic)
            confirm_message.append(_message)
            units_payload.append(n)
        else:
            _LOGGING.warning(f'Adapter {n} could not be found. Ignoring.')
    if not units_payload:
        raise click.BadArgumentUsage('No valid adapters could be found.')
    else:
        payload['units'] = units_payload
    confirm_message.append(
        'Are you sure you want to delete the following NICs'
    )
    confirm_message_str = '\n'.join(confirm_message)
    # confirm message
    confirm = confirm or click.confirm(confirm_message_str)
    # request
    if confirm:
        obj = ctx.delete_vm_nics(**payload)
    else:
        raise click.ClickException('Cancelled by user.')
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('retire', short_help='VM retirement.')
@pass_context
def compute_vm_set_retirement(ctx: Configuration):
    """Manage virtual machine retirement requests.

    Create, confirm and cancel virtual machine retirement requests.
    """
    if ctx.payload_options.get('schedule'):
        _LOGGING.warning(
            'schedule is ignored for retirement requests. Removing.'
        )
        del ctx.payload_options['schedule']


@compute_vm_set_retirement.command(
    'mk', short_help='Create retirement request.'
)
@click.option(
    '--rtype',
    '-t',
    type=click.Choice(['timedelta', 'datetime']),
    help='Retirement request type.',
    required=True,
)
@click.option(
    '--warning-days',
    '-w',
    type=click.INT,
    help='Days before retirement date to notify',
)
@click.option(
    '--value',
    '-v',
    help='Value for given retirement type. i.e. <hours>,<days>,<months>',
    required=True,
    callback=retirement_value,
)
@click.option(
    '-c', '--confirm', is_flag=True, default=False, help='Confirm no warning.'
)
@pass_context
def compute_vm_set_retirement_mk(
    ctx: Configuration, rtype, warning_days, value, confirm
):
    """Retire virtual machine on given time.

    vss-cli compute vm set <id> retire mk -t timedelta -w <days> \
    -v <hours>,<days>,<months>

    vss-cli compute vm set <id> retire mk -t datetime -w <days> \
    -v "YYYY-MM-DD HH:MM"
    """
    if rtype == 'timedelta':
        payload = dict(
            vm_id=ctx.moref,
            value=dict(hours=value[0], days=value[1], months=value[2]),
            rtype=rtype,
        )
    else:
        payload = dict(
            vm_id=ctx.moref, value=dict(datetime=value), rtype=rtype
        )
    # add if warning
    if warning_days:
        payload['warning'] = warning_days
    else:
        confirmation = confirm or click.confirm(
            'No warning will be sent for confirmation or cancellation. \n'
            'Retirement request will proceed when specified. \n'
            'Are you sure?'
        )
        if not confirmation:
            raise click.ClickException('Cancelled by user.')
    # add common options
    payload.update(ctx.payload_options)
    # submit request
    _LOGGING.debug(f'retire payload: {payload}')
    obj = ctx.retire_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_retirement.command(
    'confirm', short_help='Confirm retirement request.'
)
@click.argument(
    'request_id',
    type=click.INT,
    required=True,
    shell_complete=autocompletion.vm_retirement_requests,
)
@pass_context
def compute_vm_set_retirement_confirm(ctx: Configuration, request_id: int):
    """Confirm retirement request."""
    # create payload
    payload = dict(request_id=request_id)
    if not ctx.get_vm_retirement_requests(
        vm_id=ctx.moref, filter=f'id,eq{request_id}'
    ):
        raise click.BadArgumentUsage(
            f'Request ID {request_id} could not be found.'
        )
    # request
    obj = ctx.confirm_retirement_request(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE_CONFIRM
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_retirement.command(
    'cancel', short_help='Cancel retirement request.'
)
@click.argument(
    'request_id',
    type=click.INT,
    required=True,
    shell_complete=autocompletion.vm_retirement_requests,
)
@pass_context
def compute_vm_set_retirement_cancel(ctx: Configuration, request_id: int):
    """Cancel retirement request."""
    # create payload
    payload = dict(request_id=request_id)
    if not ctx.get_vm_retirement_requests(
        vm_id=ctx.moref, filter=f'id,eq{request_id}'
    ):
        raise click.BadArgumentUsage(
            f'Request ID {request_id} could not be found.'
        )
    # request
    obj = ctx.cancel_retirement_request(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE_CANCEL
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_retirement.command(
    'send', short_help='Send confirmation message.'
)
@click.argument(
    'request_id',
    type=click.INT,
    required=True,
    shell_complete=autocompletion.vm_retirement_requests,
)
@pass_context
def compute_vm_set_retirement_notify(ctx: Configuration, request_id: int):
    """Cancel retirement request."""
    # create payload
    payload = dict(request_id=request_id)
    if not ctx.get_vm_retirement_requests(
        vm_id=ctx.moref, filter=f'id,eq{request_id}'
    ):
        raise click.BadArgumentUsage(
            f'Request ID {request_id} could not be found.'
        )
    # request
    obj = ctx.send_confirmation_retirement_request(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_RETIRE_CANCEL
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('snapshot', short_help='Snapshot management')
@pass_context
def compute_vm_set_snapshot(ctx: Configuration):
    """Manage virtual machine snapshots.

    Create, delete and revert virtual machine snapshot on a
    given date and time.
    """
    if ctx.payload_options.get('schedule'):
        _LOGGING.warning('schedule is ignored for snapshots. Removing.')
        del ctx.payload_options['schedule']


@compute_vm_set_snapshot.command('mk', short_help='Create snapshot')
@click.option(
    '-d',
    '--description',
    type=click.STRING,
    required=True,
    help='A brief description of the snapshot.',
)
@click.option(
    '-t',
    '--timestamp',
    type=click.DateTime(formats=[const.DEFAULT_DATETIME_FMT]),
    default=datetime.datetime.strftime(
        datetime.datetime.now(), const.DEFAULT_DATETIME_FMT
    ),
    required=False,
    show_default=True,
    help='Timestamp to create the snapshot from.',
)
@click.option(
    '-l',
    '--lifetime',
    type=click.IntRange(1, 72),
    default=24,
    required=False,
    show_default=True,
    help='Number of hours the snapshot will live.',
)
@click.option(
    '-c',
    '--consolidate/--no-consolidate',
    is_flag=True,
    default=True,
    required=False,
    show_default=True,
    help='Consolidate disks after snapshot deletion',
)
@click.option(
    '-m',
    '--memory/--no-memory',
    is_flag=True,
    default=True,
    required=False,
    show_default=True,
    help='Include/exclude memory in snapshot.',
)
@pass_context
def compute_vm_set_snapshot_mk(
    ctx: Configuration, description, timestamp, lifetime, consolidate, memory
):
    """Create virtual machine snapshot.

    vss-cli compute vm set <name-or-vm_id> snapshot mk
    --description 'Short description'

    Note: if -t/--timestamp not specified, the snapshot request timestamp
    is current time.
    """
    # create payload
    payload = dict(
        vm_id=ctx.moref,
        desc=description,
        date_time=datetime.datetime.strftime(
            timestamp, const.DEFAULT_DATETIME_FMT
        ),
        valid=lifetime,
        consolidate=consolidate,
        with_memory=memory,
    )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_snapshot(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_snapshot.command('rm', short_help='Remove snapshot')
@click.argument('snapshot_id', type=click.INT, required=True)
@pass_context
def compute_vm_set_snapshot_rm(ctx: Configuration, snapshot_id):
    """Remove virtual machine snapshot.

    vss-cli compute vm set <name-or-vm_id> snapshot rm <snapshot-id>
    """
    # create payload
    payload = dict(vm_id=ctx.moref, snapshot=snapshot_id)
    if not ctx.get_vm_snapshot(vm_id=ctx.moref, snapshot=snapshot_id):
        raise click.BadArgumentUsage(
            f'Snapshot ID {snapshot_id} could not be found.'
        )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.delete_vm_snapshot(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_snapshot.command('re', short_help='Revert snapshot')
@click.argument('snapshot_id', type=click.INT, required=True)
@pass_context
def compute_vm_set_snapshot_re(ctx: Configuration, snapshot_id):
    """Revert virtual machine snapshot.

    vss-cli compute vm set <name-or-vm_id> snapshot re <snapshot-id>
    """
    # create payload
    payload = dict(vm_id=ctx.moref, snapshot=snapshot_id)
    if not ctx.get_vm_snapshot(vm_id=ctx.moref, snapshot=snapshot_id):
        raise click.BadArgumentUsage(
            f'Snapshot ID {snapshot_id} could not be found.'
        )
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.revert_vm_snapshot(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('state', short_help='Power state')
@click.argument(
    'state',
    type=click.Choice(['on', 'off', 'reboot', 'reset', 'shutdown', 'suspend']),
    required=True,
)
@click.option(
    '-c', '--confirm', is_flag=True, default=False, help='Confirm state change'
)
@pass_context
def compute_vm_set_state(ctx: Configuration, state, confirm):
    """Set given virtual machine power state.

    vss-cli compute vm set <name-or-vm_id> state on|off|reset|reboot|shutdown
    --confirm

    Reboot and shutdown send a guest OS restart signal (VMware Tools required).
    """
    # lookup dict for state
    lookup = {
        'on': 'poweredOn',
        'off': 'poweredOff',
        'reset': 'reset',
        'reboot': 'reboot',
        'shutdown': 'shutdown',
        'suspend': 'suspend',
    }
    # create payload
    payload = dict(vm_id=ctx.moref, state=lookup[state])
    # add common options
    payload.update(ctx.payload_options)
    # validate VMware tools if shutdown/reboot
    if state in ['reboot', 'shutdown']:
        vmt = ctx.get_vm_tools(ctx.moref)
        if not vmt:
            raise click.BadParameter(
                f'VMware Tools status could not be checked on {ctx.moref} '
            )
        if vmt.get('runningStatus') in ["guestToolsRunning"]:
            raise click.BadParameter(
                f'VMware Tools must be running '
                f'on {ctx.moref} send a reboot or shutdown '
                f'signal.'
            )
    # confirmation only required if state if not off
    is_powered_off = ctx.is_powered_off_vm(ctx.moref)
    if not is_powered_off:
        # process request
        # show guest os info if no confirmation flag has been
        # included - just checking
        guest_info = ctx.get_vm_guest(ctx.moref)
        ip_addresses = (
            ', '.join(guest_info.get('ip_address'))
            if guest_info.get('ip_address')
            else ''
        )
        # confirmation string
        confirmation_str = const.DEFAULT_STATE_MSG.format(
            state=state, ip_addresses=ip_addresses, **guest_info
        )
        confirmation = confirm or click.confirm(confirmation_str)
        if not confirmation:
            raise click.ClickException('Cancelled by user.')
    # request
    obj = ctx.update_vm_state(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'template', short_help='Mark vm as template or vice versa.'
)
@click.option(
    '--on/--off',
    is_flag=True,
    help='Marks vm as template or template as vm',
    default=False,
)
@pass_context
def compute_vm_set_template(ctx: Configuration, on):
    """Mark virtual machine as template or template to virtual machine.

    vss-cli compute vm set <name-or-vm_id> template --on/--off
    """
    # create payload
    payload = dict(vm_id=ctx.moref, value=on)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.mark_template_as_vm(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('tools', short_help='Manage VMware Tools')
@click.argument(
    'action', type=click.Choice(['upgrade', 'mount', 'unmount']), required=True
)
@pass_context
def compute_vm_set_tools(ctx: Configuration, action):
    """Upgrade, mount and unmount official VMware Tools package.

    This command does not apply for Open-VM-Tools.

    vss-cli compute vm set <name-or-vm_id> tools upgrade|mount|unmount
    """
    payload = dict(vm_id=ctx.moref, action=action)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_tools(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('usage', short_help='Usage (Metadata)')
@click.argument(
    'usage', type=click.Choice(['Prod', 'Test', 'Dev', 'QA']), required=True
)
@pass_context
def compute_vm_set_usage(ctx: Configuration, usage):
    """Update virtual machine usage in both name prefix and metadata.

    vss-cli compute vm set <name-or-vm_id> usage Prod|Test|Dev|QA
    """
    # create payload
    payload = dict(vm_id=ctx.moref, usage=usage)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_vss_usage(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group('version')
@pass_context
def compute_vm_set_version(ctx: Configuration):
    """Manage virtual machine virtual hardware version and policy."""


@compute_vm_set_version.command(
    'vmx', short_help='Update hardware (VMX) version'
)
@click.argument(
    'vmx',
    type=click.STRING,
    shell_complete=autocompletion.virtual_hw_types,
    required=False,
)
@pass_context
def compute_vm_set_version_policy_vmx(ctx: Configuration, vmx):
    """Update virtual hardware version."""
    # create payload
    payload = dict(vm_id=ctx.moref, vmx=vmx)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_version(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_version.command(
    'policy', short_help='Update hardware (VMX) version ' 'upgrade policy'
)
@click.argument(
    'policy',
    type=click.Choice(['never', 'onSoftPowerOff', 'always']),
    required=True,
)
@pass_context
def compute_vm_set_version_policy(ctx: Configuration, policy):
    """Update virtual hardware version upgrade policy."""
    # create payload
    payload = dict(vm_id=ctx.moref, policy=policy)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.update_vm_version_policy(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'vmrc-copy-paste', short_help='Enable or disable VMRC copy-paste settings'
)
@click.option(
    '--on/--off',
    help='Enable or disable VMRC copy-paste settings',
    default=None,
)
@pass_context
def compute_vm_set_vmrc_copy_paste(ctx: Configuration, on):
    """Enable or disable copy/paste between VMRC and VM OS."""
    # create payload
    payload = dict(vm_id=ctx.moref)
    # add common options
    payload.update(ctx.payload_options)
    # request
    if on:
        obj = ctx.enable_vm_vmrc_copy_paste(**payload)
    else:
        obj = ctx.disable_vm_vmrc_copy_paste(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command(
    'vss-option', short_help='Enable or disable given vss-option'
)
@click.argument(
    'vss-option',
    type=click.STRING,
    shell_complete=autocompletion.vss_options,
    required=False,
)
@click.option(
    '--on/--off', help='Enable or disable given vss-option', default=False
)
@pass_context
def compute_vm_set_vss_option(ctx: Configuration, vss_option, on):
    """Enable or disable given VSS Option."""
    # create payload
    payload = dict(vm_id=ctx.moref, option_name=vss_option)
    # add common options
    payload.update(ctx.payload_options)
    # request
    if on:
        obj = ctx.enable_vm_vss_option(**payload)
    else:
        obj = ctx.disable_vm_vss_option(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.command('vss-service', short_help='VSS Service name or ID')
@click.argument(
    'label-name-or-id',
    shell_complete=autocompletion.vss_services,
    type=click.STRING,
    required=True,
)
@pass_context
def compute_vm_set_vss_service(ctx: Configuration, label_name_or_id):
    """Update VSS service name or ID."""
    service = ctx.get_vss_service_by_name_label_or_id(label_name_or_id)[0][
        'id'
    ]
    # create payload
    payload = dict(vm_id=ctx.moref, service_name_or_id=service)
    # add common options
    payload.update(ctx.payload_options)
    obj = ctx.update_vm_vss_service(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set.group(
    'controller', short_help='IDE/SCSI controller management'
)
@pass_context
def compute_vm_set_controller(ctx: Configuration):
    """Manage virtual machine IDE/SCSI controllers.

    Add, update and remove controllers.
    """
    pass


@compute_vm_set_controller.group(
    'scsi', short_help='SCSI controller management'
)
@pass_context
def compute_vm_set_controller_scsi(ctx: Configuration):
    """Manage virtual machine SCSI controllers.

    Add, update and remove controllers.
    """
    pass


@compute_vm_set_controller_scsi.command(
    'mk', short_help='Create SCSI controller(s)'
)
@c_so.scsi_ctrllr_opt
@pass_context
def compute_vm_set_controller_scsi_mk(ctx: Configuration, scsi):
    """Create virtual machine SCSI controllers.

    vss-cli compute vm set <name-or-vm_id> controller scsi mk
    -s paravirtual=virtualsharing -s paravirtual
    """
    payload = dict(vm_id=ctx.moref, devices=scsi)
    # add common options
    payload.update(ctx.payload_options)
    # request
    obj = ctx.create_vm_scsi_device(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_controller_scsi.command(
    'up', short_help='Update SCSI controller'
)
@click.argument('bus_number', type=click.INT, required=True)
@click.option(
    '-t',
    '--scsi-type',
    shell_complete=autocompletion.vm_controller_scsi_types,
    required=False,
    help='Type of SCSI Controller.',
)
@click.option(
    '-s',
    '--sharing',
    shell_complete=autocompletion.vm_controller_scsi_sharing,
    required=False,
    help='Sharing mode of SCSI Controller.',
)
@pass_context
def compute_vm_set_controller_scsi_up(
    ctx: Configuration, bus_number, scsi_type, sharing
):
    """Update virtual machine SCSI controller type.

    vss-cli compute vm set <name-or-vm_id> controller scsi up
    <bus> -t paravirtual

    vss-cli compute vm set <name-or-vm_id> controller scsi up
    <bus> -s nosharing
    """
    # validate if unit exists
    bus = ctx.get_vm_scsi_device(ctx.moref, bus_number)
    if not bus:
        raise click.BadOptionUsage('', 'SCSI bus could not be found.')
    payload = dict(vm_id=ctx.moref, bus=bus_number)
    # add common options
    payload.update(ctx.payload_options)
    if scsi_type is not None:
        payload['bus_type'] = scsi_type
        obj = ctx.update_vm_scsi_device_type(**payload)
    elif sharing is not None:
        payload['sharing'] = sharing
        obj = ctx.update_vm_scsi_device_sharing(**payload)
    else:
        raise click.BadOptionUsage(
            '', 'Either -t/--scsi-type or -s/--sharing is required.'
        )
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_set_controller_scsi.command(
    'rm', short_help='Remove SCSI controller(s)'
)
@click.argument('bus_number', type=click.INT, required=True, nargs=-1)
@click.option(
    '-r',
    '--rm',
    is_flag=True,
    default=False,
    help='Confirm controller removal',
)
@pass_context
def compute_vm_set_controller_scsi_rm(ctx: Configuration, bus_number, rm):
    """Remove virtual machine SCSI controllers.

    vss-cli compute vm set <name-or-vm_id> controller scsi rm <bus> ...
    """
    buses = list(bus_number)
    for bus in buses:
        _bus = ctx.get_vm_scsi_device(ctx.moref, bus)
        if not _bus:
            buses.remove(bus)
            _LOGGING.warning(
                f'Ignoring SCSI Controller {bus}. Could not be found.'
            )
        else:
            devices = ctx.get_vm_disk_by_scsi_device(ctx.moref, bus)
            if devices:
                buses.remove(bus)
                _LOGGING.warning(
                    f'Ignoring SCSI Controller {bus}. '
                    f'Device has {len(devices)} disk(s) attached.'
                )
    if not buses:
        raise click.BadArgumentUsage(
            'No valid SCSI Controllers could be found'
        )
    payload = dict(vm_id=ctx.moref, buses=buses)
    # add common options
    payload.update(ctx.payload_options)
    # confirm
    confirm = rm or click.confirm(
        f'Are you sure you want to remove SCSI bus {buses}?'
    )
    if confirm:
        obj = ctx.delete_vm_scsi_devices(**payload)
    else:
        raise click.ClickException('Cancelled by user.')
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm.group(
    'rm', help='Delete given virtual machines', invoke_without_command=True
)
@click.option(
    '-f',
    '--force',
    is_flag=True,
    default=False,
    show_default=True,
    help='Force deletion if power state is on',
)
@click.option(
    '-p',
    '--prune',
    is_flag=True,
    default=False,
    show_default=True,
    help='Prune virtual machine.',
)
@click.option(
    '-s',
    '--show-info',
    is_flag=True,
    default=False,
    show_default=True,
    help='Show guest info and confirmation if -f/--force is not included.',
)
@click.argument(
    'vm_id',
    type=click.STRING,
    required=True,
    nargs=-1,
    shell_complete=autocompletion.virtual_machines,
)
@so.max_del_opt
@pass_context
def compute_vm_rm(
    ctx: Configuration,
    vm_id: list,
    max_del: int,
    force: bool,
    show_info: bool,
    prune: bool,
):
    """Delete a list of virtual machine ids.

    vss-cli compute vm rm <name-or-vm-id> <name-or-vm-id> --show-info
    """
    _LOGGING.debug(f'Attempting to remove {vm_id}')
    # whether to wait for requests
    if len(vm_id) > max_del:
        raise click.BadArgumentUsage(
            'Increase max instance removal with --max-del/-m option'
        )
    # result
    objs = list()
    with ctx.spinner(disable=ctx.debug or show_info):
        for vm in vm_id:
            skip = False
            _vm = ctx.get_vm_by_id_or_name(vm)
            if not _vm:
                _LOGGING.warning(
                    f'Virtual machine {vm} could not be found. Skipping.'
                )
                skip = True
            _LOGGING.debug(f'Found {_vm}')
            moref = _vm[0]['moref']
            if _vm and show_info:
                c_str = const.DEFAULT_VM_DEL_MSG.format(vm=_vm[0])
                confirmation = force or click.confirm(c_str)
                if not confirmation:
                    _LOGGING.warning(f'Skipping {moref}...')
                    skip = True
            if not skip:
                # request
                payload = dict(vm_id=moref, force=force)
                if prune:
                    payload['prune'] = True
                objs.append(ctx.delete_vm(**payload))
    # print
    if objs:
        columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
        ctx.echo(
            format_output(ctx, objs, columns=columns, single=len(objs) == 1)
        )
        if ctx.wait_for_requests:
            if len(objs) > 1:
                ctx.wait_for_requests_to(objs, in_multiple=True)
            else:
                ctx.wait_for_request_to(objs[0])
    else:
        _LOGGING.warning('No requests have been submitted.')


@compute_vm.group(
    'mk', short_help='Create virtual machine', invoke_without_command=True
)
@click.option(
    '-u',
    '--user-meta',
    help='User metadata in key=value format. '
    'These tags are stored in the request.',
    required=False,
    default=None,
)
@so.dry_run_opt
@pass_context
def compute_vm_mk(ctx: Configuration, user_meta: str, dry_run: bool):
    """Deploy Virtual machines."""
    ctx.user_meta = dict(to_tuples(user_meta))
    ctx.tmp = dry_run
    if user_meta:
        ctx.payload_options['user_meta'] = ctx.user_meta
    if click.get_current_context().invoked_subcommand is None:
        raise click.UsageError('Sub command is required')


@compute_vm_mk.command(
    'from-file',
    short_help='Create virtual machine from VSS CLI specification.',
)
@click.argument('file-spec', type=click.File('r'), required=False)
@click.option(
    '-t',
    '--spec-template',
    required=False,
    type=click.Choice(['shell']),
    help='Specification template to load and edit.',
)
@click.option(
    '-e',
    '--edit',
    is_flag=True,
    required=False,
    help='Edit before submitting request',
)
@click.option(
    '--save',
    '-s',
    default=False,
    is_flag=True,
    help='Save file after editing.',
)
@pass_context
def compute_vm_from_file(
    ctx: Configuration, file_spec, edit, spec_template, save
):
    """Create virtual machine from VSS CLI file specification.

    Run the following command to deploy a vm based on a
    VSS CLI specification template:

    vss-cli compute vm mk from-file -s -t shell -e vm.yaml

    Or from an existing vm:

    vss-cli compute vm get <name-or-vm_id> spec --edit vm.yaml

    Edit vm.yaml file and deploy as follows:

    vss-cli compute vm mk from-file <cli-spec>.json|yaml

    """
    import time
    from pick import pick

    if file_spec:
        raw = file_spec.read()
    else:
        # load default configuration
        if not spec_template:
            message = (
                'Please choose a template to load '
                '(press SPACE to mark, ENTER to continue): '
            )
            spec_template, index = pick(['shell'], message)
        file_spec = os.path.join(
            const.DEFAULT_DATA_PATH, f'{spec_template}.yaml'
        )
        # proceed to load file
        with open(file_spec) as data_file:
            raw = data_file.read()
    # whether to launch the editor and save file
    # before submitting request
    if edit:
        # launch editor
        new_raw = click.edit(raw, extension='.yaml')
        # load object
        if new_raw and save:
            new_obj = ctx.yaml_load(new_raw)
            file_name = f'from-file-{int(time.time())}.yaml'
            _LOGGING.debug(f'Saving spec to {file_name}')
            with open(file_name, 'w') as fp:
                ctx.yaml_dump_stream(new_obj, stream=fp)
            raw = new_raw
        else:
            _LOGGING.warning('Editor contents will not be saved.')

    payload = ctx.yaml_load(raw)
    _LOGGING.debug(f'Payload from raw: f{payload}')
    # add common options
    spec_payload = dict()
    spec_payload.update(ctx.payload_options)
    if payload['built'] == 'os_install':
        spec_payload = ctx.get_api_spec_from_cli_spec(
            payload=payload, built='os_install'
        )
    else:
        raise click.UsageError('Not yet implemented.')
    # request
    ctx.dry_run = ctx.tmp
    obj = ctx.create_vm(**spec_payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_mk.command(
    'from-spec', short_help='Create vm from another vm spec'
)
@c_so.source_opt
@c_so.description_opt
@c_so.client_nr_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_nr_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.cpu_cps_opt
@c_so.folder_nr_opt
@c_so.scsi_ctrllr_nr_opt
@c_so.disks_nr_opt
@c_so.networks_nr_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.iso_opt
@c_so.extra_config_opt
@c_so.power_on_opt
@c_so.template_opt
@c_so.vss_service_opt
@c_so.instances
@c_so.firmware_nr_opt
@c_so.retire_type
@c_so.retire_warning
@c_so.retire_value
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_vm_mk_spec(
    ctx: Configuration,
    name,
    source,
    description,
    client,
    usage,
    memory,
    cpu,
    cores_per_socket,
    folder,
    scsi,
    disk,
    notes,
    admin,
    inform,
    iso,
    net,
    domain,
    os,
    extra_config,
    power_on,
    template,
    vss_service,
    instances,
    firmware,
    retire_type,
    retire_warning,
    retire_value,
):
    """Create vm based on another vm configuration specification.

    This command takes the vm specification
    (memory, disk, networking, etc) as a
    base for a new VM.
    """
    built = 'os_install'
    _vm = ctx.get_vm_by_id_or_name(source)
    vm_id = _vm[0]['moref']
    s_payload = ctx.get_vm_spec(vm_id)
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        built=built,
        power_on=power_on,
        template=template,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = {
            'count': cpu,
            'cores_per_socket': cores_per_socket or 1,
        }
    if scsi:
        payload['scsi'] = list(scsi)
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    if iso:
        _iso = ctx.get_iso_by_name_or_path(iso)
        payload['iso'] = _iso[0]['path']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if client:
        payload['client'] = client
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if firmware:
        _firmw = ctx.get_vm_firmware_by_type_or_desc(firmware)
        payload['firmware'] = _firmw[0]['type']
    # retirement
    if retire_value or retire_type or retire_warning:
        retire = process_retirement_new(
            retire_type, retire_value, retire_warning
        )
        payload['retirement'] = retire
    # updating spec with new vm spec
    s_payload.update(payload)
    _LOGGING.debug(f'source={s_payload}')
    _LOGGING.debug(f'spec={payload}')
    payload = s_payload
    _LOGGING.debug(f'final spec={payload}')
    # request
    if instances > 1:
        payload['count'] = instances
        obj = ctx.create_vms(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        obj = ctx.create_vm(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command('shell', short_help='Create empty virtual machine')
@c_so.description_opt
@c_so.client_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.cpu_cps_opt
@c_so.folder_opt
@c_so.scsi_ctrllr_nr_opt
@c_so.disk_opt
@c_so.networks_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.iso_opt
@c_so.extra_config_opt
@c_so.power_on_opt
@c_so.template_opt
@c_so.vss_service_opt
@c_so.instances
@c_so.firmware_nr_opt
@c_so.retire_type
@c_so.retire_warning
@c_so.retire_value
@click.argument('name', type=click.STRING, required=True)
@pass_context
def compute_vm_mk_shell(
    ctx: Configuration,
    name,
    description,
    client,
    usage,
    memory,
    cpu,
    cores_per_socket,
    folder,
    scsi,
    disk,
    notes,
    admin,
    inform,
    iso,
    net,
    domain,
    os,
    extra_config,
    power_on,
    template,
    vss_service,
    instances,
    firmware,
    retire_type,
    retire_warning,
    retire_value,
):
    """Create a new VM with no operating system pre-installed."""
    built = 'os_install'
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        built=built,
        power_on=power_on,
        template=template,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = {
            'count': cpu,
            'cores_per_socket': cores_per_socket or 1,
        }
    if scsi:
        payload['scsi'] = scsi
    if disk:
        payload['disks'] = disk
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    if iso:
        _iso = ctx.get_iso_by_name_or_path(iso)
        payload['iso'] = _iso[0]['path']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if client:
        payload['client'] = client
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if firmware:
        _firmw = ctx.get_vm_firmware_by_type_or_desc(firmware)
        payload['firmware'] = _firmw[0]['type']
    # retirement
    if retire_value or retire_type or retire_warning:
        retire = process_retirement_new(
            retire_type, retire_value, retire_warning
        )
        payload['retirement'] = retire
    _LOGGING.debug(f'payload: {payload}')
    # request
    if instances > 1:
        payload['count'] = instances
        obj = ctx.create_vms(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        obj = ctx.create_vm(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command('from-template', short_help='Create vm from template')
@c_so.source_template_opt
@c_so.description_opt
@c_so.client_nr_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_nr_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.cpu_cps_opt
@c_so.folder_nr_opt
@c_so.scsi_ctrllr_nr_opt
@c_so.disks_nr_opt
@c_so.networks_nr_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.power_on_opt
@c_so.template_opt
@c_so.vss_service_opt
@c_so.instances
@c_so.firmware_nr_opt
@c_so.retire_type
@c_so.retire_warning
@c_so.retire_value
@click.argument('name', type=click.STRING, required=False)
@pass_context
def compute_vm_mk_template(
    ctx: Configuration,
    name,
    source,
    description,
    client,
    usage,
    memory,
    cpu,
    cores_per_socket,
    folder,
    scsi,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    extra_config,
    vss_service,
    power_on,
    template,
    firmware,
    instances,
    retire_type,
    retire_warning,
    retire_value,
):
    """Deploy virtual machine from template."""
    # get source from uuid or name
    _vm = ctx.get_vm_by_id_or_name(source)
    vm_id = _vm[0]['moref']
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        source_template=vm_id,
        power_on=power_on,
        template=template,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = {
            'count': cpu,
            'cores_per_socket': cores_per_socket or 1,
        }
    if scsi:
        payload['scsi'] = list(scsi)
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if client:
        payload['client'] = client
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if custom_spec:
        payload['custom_spec'] = custom_spec
    if firmware:
        _firmw = ctx.get_vm_firmware_by_type_or_desc(firmware)
        payload['firmware'] = _firmw[0]['type']
    # retirement
    if retire_value or retire_type or retire_warning:
        retire = process_retirement_new(
            retire_type, retire_value, retire_warning
        )
        payload['retirement'] = retire
    # request
    if instances > 1:
        payload['count'] = instances
        obj = ctx.deploy_vms_from_template(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        obj = ctx.deploy_vm_from_template(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command('from-clone', short_help='Create vm from clone')
@c_so.source_opt
@c_so.description_opt
@c_so.client_nr_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_nr_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.cpu_cps_opt
@c_so.folder_nr_opt
@c_so.scsi_ctrllr_nr_opt
@c_so.disks_nr_opt
@c_so.networks_nr_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.power_on_opt
@c_so.template_opt
@c_so.vss_service_opt
@c_so.instances
@c_so.firmware_nr_opt
@c_so.snapshot
@c_so.retire_type
@c_so.retire_warning
@c_so.retire_value
@click.argument('name', type=click.STRING, required=False)
@pass_context
def compute_vm_mk_clone(
    ctx: Configuration,
    name,
    source,
    description,
    client,
    usage,
    memory,
    cpu,
    cores_per_socket,
    folder,
    scsi,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    extra_config,
    power_on,
    template,
    vss_service,
    instances,
    firmware,
    snapshot,
    retire_type,
    retire_warning,
    retire_value,
):
    """Clone virtual machine from running or powered off vm.

    If name argument is not specified, -clone suffix will be added to
    resulting virtual machine.
    """
    # get source from uuid or name
    _vm = ctx.get_vm_by_id_or_name(source)
    vm_id = _vm[0]['moref']
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        source=vm_id,
        power_on=power_on,
        template=template,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = {
            'count': cpu,
            'cores_per_socket': cores_per_socket or 1,
        }
    if scsi:
        payload['scsi'] = scsi
    if disk:
        payload['disks'] = list(disk)
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if client:
        payload['client'] = client
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if custom_spec:
        payload['custom_spec'] = custom_spec
    if firmware:
        _firmw = ctx.get_vm_firmware_by_type_or_desc(firmware)
        payload['firmware'] = _firmw[0]['type']
    if snapshot:
        _snap = ctx.get_vm_snapshot_by_id_name_or_desc(vm_id, snapshot)
        payload['source_snap_id'] = _snap[0]['id']
    # retirement
    if retire_value or retire_type or retire_warning:
        retire = process_retirement_new(
            retire_type, retire_value, retire_warning
        )
        payload['retirement'] = retire
    if instances > 1:
        payload['count'] = instances
        obj = ctx.create_vms_from_clone(**payload)
        _columns = const.COLUMNS_REQUEST_MULT_SUBMITTED
    else:
        # request
        obj = ctx.create_vm_from_clone(**payload)
        _columns = const.COLUMNS_REQUEST_SUBMITTED
    # print
    columns = ctx.columns or _columns
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        if instances > 1:
            ctx.wait_for_requests_to(obj)
        else:
            ctx.wait_for_request_to(obj)


@compute_vm_mk.command(
    'from-image', short_help='Create vm from OVA/OVF image.'
)
@click.argument('name', type=click.STRING, required=False)
@c_so.source_image_opt
@c_so.description_opt
@c_so.client_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.cpu_cps_opt
@c_so.folder_opt
@c_so.scsi_ctrllr_nr_opt
@c_so.disk_opt
@c_so.networks_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.power_on_opt
@c_so.template_opt
@c_so.user_data_opt
@c_so.net_cfg_opt
@c_so.vss_service_opt
@c_so.firmware_nr_opt
@c_so.retire_type
@c_so.retire_warning
@c_so.retire_value
@pass_context
def compute_vm_mk_image(
    ctx: Configuration,
    name,
    source,
    description,
    client,
    usage,
    memory,
    cpu,
    cores_per_socket,
    folder,
    scsi,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    power_on,
    template,
    extra_config,
    user_data,
    network_config,
    vss_service,
    firmware,
    retire_type,
    retire_warning,
    retire_value,
):
    """Deploy virtual machine from image."""
    # get reference to image by
    image_ref = ctx.get_vm_image_by_name_or_id_path(source)
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        client=client,
        image=image_ref[0]['path'],
        power_on=power_on,
        template=template,
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = {
            'count': cpu,
            'cores_per_socket': cores_per_socket or 1,
        }
    if disk:
        payload['disks'] = disk
    if scsi:
        payload['scsi'] = scsi
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if custom_spec:
        payload['custom_spec'] = custom_spec
    if user_data:
        # Cloud-init nocloud config drive
        udata_pload = {
            'userdata': user_data[0],
            'userdata_encoding': user_data[1],
        }
        if network_config is not None:
            udata_pload['networkconfig'] = network_config[0]
            udata_pload['networkconfig_encoding'] = network_config[1]
        _LOGGING.debug(f'User data paylaod {udata_pload}')
        payload['user_data'] = udata_pload
    if firmware:
        _firmw = ctx.get_vm_firmware_by_type_or_desc(firmware)
        payload['firmware'] = _firmw[0]['type']
    # retirement
    if retire_value or retire_type or retire_warning:
        retire = process_retirement_new(
            retire_type, retire_value, retire_warning
        )
        payload['retirement'] = retire
    # request
    obj = ctx.create_vm_from_image(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)


@compute_vm_mk.command(
    'from-clib', short_help='Create vm from Content Library item.'
)
@click.argument('name', type=click.STRING, required=False)
@c_so.source_clib_opt
@c_so.description_opt
@c_so.client_opt
@c_so.admin_opt
@c_so.inform_opt
@c_so.usage_opt
@c_so.os_opt
@c_so.memory_opt
@c_so.cpu_opt
@c_so.cpu_cps_opt
@c_so.folder_opt
@c_so.scsi_ctrllr_nr_opt
@c_so.disks_nr_opt
@c_so.networks_opt
@c_so.domain_opt
@c_so.notes_opt
@c_so.custom_spec_opt
@c_so.extra_config_opt
@c_so.additional_parameters_opt
@c_so.power_on_opt
@c_so.template_opt
@c_so.user_data_opt
@c_so.net_cfg_opt
@c_so.vss_service_opt
@c_so.firmware_nr_opt
@c_so.retire_type
@c_so.retire_warning
@c_so.retire_value
@pass_context
def compute_vm_mk_clib(
    ctx: Configuration,
    name,
    source,
    description,
    client,
    usage,
    memory,
    cpu,
    cores_per_socket,
    folder,
    scsi,
    disk,
    notes,
    admin,
    inform,
    net,
    domain,
    os,
    custom_spec,
    power_on,
    template,
    extra_config,
    additional_params,
    user_data,
    network_config,
    vss_service,
    firmware,
    retire_type,
    retire_warning,
    retire_value,
):
    """Deploy virtual machine from Content Library."""
    item_ref = ctx.get_clib_deployable_item_by_name_or_id_path(source)
    # payload
    payload = dict(
        description=description,
        name=name,
        usage=usage,
        client=client,
        item_id=item_ref[0]['id'],
        power_on=power_on,
        template=template,
        disks=disk or [],
    )
    # Hardware
    if memory:
        payload['memory'] = memory
    if cpu:
        payload['cpu'] = {
            'count': cpu,
            'cores_per_socket': cores_per_socket or 1,
        }
    if scsi:
        payload['scsi'] = scsi
    if net:
        payload['networks'] = net
    if os:
        _os = ctx.get_os_by_name_or_guest(os)
        payload['os'] = _os[0]['guest_id']
    # Logical
    if folder:
        _folder = ctx.get_folder_by_name_or_moref_path(folder)
        payload['folder'] = _folder[0]['moref']
    if domain:
        _domain = ctx.get_domain_by_name_or_moref(domain)
        payload['domain'] = _domain[0]['moref']
    # Metadata
    if notes:
        payload['notes'] = notes
    if admin:
        name, phone, email = admin.split(':')
        payload['admin_email'] = email
        payload['admin_phone'] = phone
        payload['admin_name'] = name
    if inform:
        payload['inform'] = inform
    if vss_service:
        _svc = ctx.get_vss_service_by_name_label_or_id(vss_service)
        payload['vss_service'] = _svc[0]['id']
    # Advanced
    if extra_config:
        payload['extra_config'] = extra_config
    if additional_params:
        payload['additional_parameters'] = additional_params
    if custom_spec:
        payload['custom_spec'] = custom_spec
    if user_data:
        # Cloud-init nocloud config drive
        udata_pload = {
            'userdata': user_data[0],
            'userdata_encoding': user_data[1],
        }
        if network_config is not None:
            udata_pload['networkconfig'] = network_config[0]
            udata_pload['networkconfig_encoding'] = network_config[1]
        _LOGGING.debug(f'User data paylaod {udata_pload}')
        payload['user_data'] = udata_pload
    if firmware:
        _firmw = ctx.get_vm_firmware_by_type_or_desc(firmware)
        payload['firmware'] = _firmw[0]['type']
    # retirement
    if retire_value or retire_type or retire_warning:
        retire = process_retirement_new(
            retire_type, retire_value, retire_warning
        )
        payload['retirement'] = retire
    # request
    obj = ctx.deploy_vm_from_clib_item(**payload)
    # print
    columns = ctx.columns or const.COLUMNS_REQUEST_SUBMITTED
    ctx.echo(format_output(ctx, [obj], columns=columns, single=True))
    # wait for request
    if ctx.wait_for_requests:
        ctx.wait_for_request_to(obj)
