from __future__ import print_function

from datetime import datetime
from warnings import warn
import argparse
import os
import traceback
import stat
import sys

from . import settings
from .diskemptysampler import DiskEmptySampler
from .hdddock import BaseStorageDevice
from .inventoryrestclient import InventoryRESTClient
from .labelprinterapiclient import get_labelprinter


S_UNSET = '(unset)'

try:
    raw_input  # py2
except NameError:
    def raw_input(msg=None):  # py3
        if msg is not None:
            print(msg, end='')
        return input()


class Inventory:
    def __init__(self, inventory_rest_client, hdd_id):
        self._client = inventory_rest_client
        self._hdd_id = hdd_id
        self.flush()

    def flush(self):
        self._data = self._client.get_hdd(self._hdd_id)[0]

    @property
    def id(self):
        return self._data['id']

    @property
    def tag_uid(self):
        return self._data['tag_uid']

    @property
    def bay(self):
        return self._data['bay']

    @property
    def current_owner(self):
        return (self._data.get('current_owner') or {}).get('name')

    @property
    def current_health_status(self):
        return (self._data.get('current_health') or {}).get('status')


class SymlinkNotFound(Exception):
    pass


class DeviceManager(object):
    def __init__(self, hdd_dock, hdd_id, inventory_rest_client,
                 author, location):
        self._hdd_dock = hdd_dock
        self._hdd_id = hdd_id
        self._inventory_rest_client = inventory_rest_client
        self._author = author
        self._location = location

    def show_summary(self, print_data):
        do_print(print_data, self._hdd_dock)

    def show_commands(self):
        erase_methods = self._hdd_dock.get_erase_methods()
        next_erase_method = 0

        print('')
        print('Inventory-url: {}'.format(
            self._inventory_rest_client.get_hdd_url(self._hdd_id)))
        print('')
        print('Possible actions:')
        print('1. Change owner')
        print('2. Reprint label')
        print('3. Quick erase')
        if len(erase_methods) > 1:
            print('4. Secure erase ({})'.format(
                erase_methods[next_erase_method].name))
            next_erase_method += 1
        print('5. Change server bay')
        print('6. Change health status')
        print('7. Print health label')
        print('8. Secure erase ({})'.format(
            erase_methods[next_erase_method].name))
        print('D. Dispose HDD in security container')
        print('P. Show current info/status (again)')

        print('')
        print('9. Quit + EJECT (^C to skip eject)')

    def _set_status(self, status, extra_info):
        self._inventory_rest_client.add_status(
            self._hdd_id, status=status, extra_info=extra_info)

    def _set_health(self, title):
        # title = 'SECURE ERASED' or ...
        health = (
            'OK' if self._hdd_dock.hwdata.wear_health_percent >= 100
            else '{}%'.format(self._hdd_dock.hwdata.wear_health_percent))
        health_status = f'health {health} - {title}'
        self.set_health(health_status)

    def set_health(self, health_status):
        self._inventory_rest_client.add_health_status(
            self._hdd_id, status=health_status,
            extra_info='--{}'.format(self._author))

    def set_health_with_wear(self, title):
        self._set_health(title)

    def quick_erase(self):
        print('Start quick wiping')
        self._hdd_dock.quick_erase()
        self._set_status('QUICK_WIPED', 'Quick wiped at {} --{}'.format(
            self._location, self._author))
        try:
            self._hdd_dock.flush()
        finally:
            self._set_health('QUICK WIPED')
        print('Disk/ssd quick wiped')

    def best_erase(self):
        erase_method = self._hdd_dock.get_erase_methods()[0]
        self._erase(erase_method)

    def second_best_erase(self):
        erase_methods = self._hdd_dock.get_erase_methods()
        if len(erase_methods) > 1:
            erase_methods.pop(0)
        self._erase(erase_methods[0])

    def _erase(self, erase_method):
        if erase_method.type == 'builtin':
            return self._erase_with_status(erase_method)
        if erase_method.type == 'manual':
            print('Secure disk wipe chosen. Please wait as this will '
                  'take a long time... - 1 pass lessrandom and 1 pass '
                  'zerofill\n')
            return self._erase_with_status(erase_method)
        raise NotImplementedError(erase_method)

    def _erase_with_status(self, erase_method):
        # Fetch vars.
        # XXX: better dynamic value for sample count based on disk size?
        sample_count = settings.POST_WIPE_SAMPLE_COUNT
        if self._hdd_dock.is_ssd():
            sample_count *= 10  # SSDs/NVMes are fast(er)
        sample_size = settings.POST_WIPE_SAMPLE_SIZE

        print('Attempting erase method {!r} on BLKDEV {!r}'.format(
            erase_method.name, self._hdd_dock.devname))

        # Running pre-sample.  This is not needed, but nice during dev.
        print(
            'DEBUG: Sampling block device to check if empty... '
            '(sample_count: {}, sample_size {})'.format(
                sample_count, sample_size))
        sampler = DiskEmptySampler(
            self._hdd_dock.devname, sample_count, sample_size)
        sampler.sample()
        if sampler.is_zero():
            print('DEBUG: No non-zero sample found. Disk already zeroed?')
        else:
            print('DEBUG: Found non-zero samples before wipe (expected)')

        print('Start secure wiping BLKDEV')
        success, error = erase_method()
        if not success:
            print('Error: {}'.format(error))
            self._set_status(
                'BLKDEV_SECURE_WIPED_ERROR', (
                    'Block device secure wipe error at {}: {} --{}'
                    .format(self._location, error, self._author)))
            self._set_health('ERASE ERROR')
            return

        print('Block device securely wiped')

        # Running post-sample. Should be all zero.
        print('DEBUG: Sampling block device afterwards...')
        sampler.sample()
        if sampler.is_zero():
            print('OK: All samples are empty')
        elif sampler.is_different():
            print(
                '(probably) OK: All samples are different '
                '(old school crypto disk?)')
        else:
            print('ERROR: Found not-wiped sample!')
            print('Please check {!r} manually!'.format(self._hdd_dock.devname))
            self._set_status(
                'BLKDEV_SECURE_WIPED_ERROR', (
                    'Block device secure wipe {!r} error at {}, non-empty '
                    'samples found --{}'
                    .format(erase_method.name, self._location, self._author)))
            self._set_health('ERASE ERROR')
            return

        # All good!
        self._set_status(
            'BLKDEV_SECURE_WIPED', (
                'Block device secure wiped using {!r} at {} and '
                'checked {}x{} --{}'
                .format(
                    erase_method.name, self._location, sample_count,
                    sample_size, self._author)))
        try:
            self._hdd_dock.flush()
        finally:
            self._set_health('SECURE ERASED')

    def _find_non_zero_blocks(self, sample_count, sample_size):

        disk_empty_sampler = DiskEmptySampler(
            self._hdd_dock.devname, sample_count, sample_size)
        result = disk_empty_sampler.sample_disk()
        assert result is not None

        return result is False  # false = we found non-zero


def register_disk(**kwargs):
    # Python2-compatible forced kwargs. Temporary fix until we clean up this
    # code.
    hdd_dock = kwargs.pop('hdd_dock')
    inventory_rest_client = kwargs.pop('inventory_rest_client')
    author = kwargs.pop('author')
    location = kwargs.pop('location')
    assert not kwargs, None

    print('')
    print('Disk is not registered yet, please specify the following fields:')
    owner = raw_input('Owner [OSSO]: ')

    # Default to OSSO
    if owner in (None, ''):
        owner = 'OSSO'

    bay = raw_input('bay ['']: ')

    if bay in (None, ''):
        bay = ''

    erase = None
    while erase not in ('y', 'n', 'Y', 'N', ''):
        erase = raw_input('Quick erase? (y/N): ')

    result = inventory_rest_client.add_hdd(hdd_dock, bay)
    tag_uid = result['tag_uid']
    hdd_id = result['id']

    inventory_rest_client.add_smart_data(
        hdd_id, rawdata=hdd_dock.hwdata.rawdata)
    inventory_rest_client.add_status(
        hdd_id, status='REGISTERED',
        extra_info='Registered at {} --{}'.format(location, author))
    inventory_rest_client.add_owner(  # XXX: author-of-owner, not owner-eml
        hdd_id, name=owner, email=author)
    inventory_rest_client.add_location(
        hdd_id, location=location)

    if erase == 'y' or erase == 'Y':
        manager = DeviceManager(
            hdd_dock, hdd_id, inventory_rest_client, author, location)
        manager.quick_erase()

    # Print label, unless the disk is in a remote machine
    if location != 'remote':
        labelprinter_rest_client = get_labelprinter()
        labelprinter_rest_client.print_hdd_label(
            tag_uid, hdd_dock.get_serial_number(), owner)

    raw_input('Registration complete, press enter')


def registered_disk_actions(**kwargs):
    # Python2-compatible forced kwargs. Temporary fix until we clean up this
    # code.
    hdd_dock = kwargs.pop('hdd_dock')
    hdd_id = kwargs.pop('hdd_id')
    inventory_rest_client = kwargs.pop('inventory_rest_client')
    static_data = kwargs.pop('static_data')
    del static_data
    dynamic_data = kwargs.pop('dynamic_data')
    author = kwargs.pop('author')
    location = kwargs.pop('location')
    assert not kwargs, None

    if not settings.DEBUG:
        # Always add smart data, even when disk is registered
        inventory_rest_client.add_smart_data(
            hdd_id, rawdata=hdd_dock.hwdata.rawdata)
        # Always add a status & location
        # of the disk being seen at OSSO HQ
        if location != 'remote':
            inventory_rest_client.add_status(
                hdd_id, status='CHECKED_IN',
                extra_info='Checked in at {} --{}'.format(location, author))
            inventory_rest_client.add_location(
                hdd_id, location=location)

    inventory = Inventory(inventory_rest_client, hdd_id)

    def _build_print_data():
        static_data, dynamic_data = build_hdd_info(hdd_dock)
        print_data = static_data + dynamic_data
        print_data.append(['', None])
        print_data.append(['REGISTRATION INFORMATION', None])
        print_data.append(['=', None])
        print_data.append(['Disk is already registered as', inventory.id])
        print_data.append(['Last owner', inventory.current_owner or S_UNSET])
        print_data.append([
            'Last health status', inventory.current_health_status or S_UNSET])
        print_data.append(['Server bay', inventory.bay or S_UNSET])
        return print_data

    manager = DeviceManager(
        hdd_dock, hdd_id, inventory_rest_client, author, location)
    manager.show_summary(_build_print_data())
    manager.show_commands()

    while True:
        action = raw_input('\nAction: ').upper()

        if action == '1':
            owner = ''
            while len(owner) == 0:
                owner = raw_input('New owner: ')
            inventory_rest_client.add_owner(  # XXX: not email-of-owner
                hdd_id, name=owner, email=author)
            inventory.flush()

        elif action == '2':
            # Print label
            labelprinter_rest_client = get_labelprinter()
            labelprinter_rest_client.print_hdd_label(
                inventory.tag_uid, hdd_dock.get_serial_number(),
                inventory.current_owner)

        elif action == '3':
            manager.quick_erase()
            inventory.flush()

        elif action == '4':
            manager.best_erase()
            inventory.flush()

        elif action == '5':
            bay = ''
            while len(bay) == 0:
                bay = raw_input('New server bay: ')
            inventory_rest_client.change_bay(hdd_id, bay)
            inventory.flush()
            print('Server bay changed to: {}'.format(inventory.bay))

        elif action == '6':
            health_status = (
                raw_input('Manual health status [ONLINE]: ') or 'ONLINE')
            manager.set_health_with_wear(health_status)
            inventory.flush()

        elif action == '7':
            # Print label
            print_health_label(hdd_dock, inventory, author, dynamic_data)

        elif action == '8':
            manager.second_best_erase()
            inventory.flush()

        elif action == '9':
            break  # Quit + EJECT

        elif action == 'D':
            assert location != 'remote', 'Cannot remote-dispose..'
            inventory_rest_client.add_status(
                hdd_id, status='HDD_DISPOSED',
                extra_info='Disposed in security container at {} --{}'.format(
                    location, author))
            inventory_rest_client.add_location(
                hdd_id, location='OSSO HQ: HDD security container')
            inventory.flush()
            break

        elif action == 'P':
            manager.show_summary(_build_print_data())
            manager.show_commands()

        else:
            print('Notice: {!r} action unknown'.format(action))

    hdd_dock.shutdown_disk()
    exit(0)


def human_readable_bytes(byte_count):
    options = ['Bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB']

    counter = 0
    while byte_count // 1024 > 0:
        byte_count = byte_count / 1024.0
        counter += 1
        if counter == len(options) - 1:
            break

    return '{} {}'.format(round(byte_count, 2), options[counter])


def do_print(data, hdd_dock):
    key_length = 0
    item_length = 0

    for key, item in data:
        key_length = max(key_length, len(key))
        item_length = max(item_length, len(item or ''))
    heading = '=' * (key_length + item_length + 3)
    fmt = '{:%d} : {}' % (key_length,)

    print('DISK INFORMATION [BAY NR: {}]'.format(
        hdd_dock.docktool_bay_nr))
    print(heading)

    for key, item in data:
        if item is None and key == '=':
            print(heading)
        elif item is None:
            print(key)
        else:
            print(fmt.format(key, item))


def print_health_label(hdd_dock, inventory, author, dynamic_data):
    """
    Print health status on a label. See also print_health_label_from_db.
    Both would like some refactoring.
    """
    today = datetime.now().strftime('%Y-%m-%d')
    # XXX: don't use dynamic_data please :(
    total_bytes_written = [
        x for x in dynamic_data
        if 'Total bytes written' in x[0]][0]
    total_bytes_read = [
        x for x in dynamic_data
        if 'Total bytes read' in x[0]][0]

    lines = [
        'Health status : {}'.format(
            inventory.current_health_status.upper()),
        '',
        'Serial : {}'.format(hdd_dock.get_serial_number()),
        'Total bytes written/read : {}/{}'.format(
            total_bytes_written[1], total_bytes_read[1]),
        'Power on hours : {} hours'.format(
            hdd_dock.hwdata.power_on_hours or S_UNSET),
        f'--{author} @ {today}',
    ]
    try:
        labelprinter_rest_client = get_labelprinter()
        labelprinter_rest_client.print_generic_label(lines)
    except Exception:
        print('Would have printed:')
        print('\n'.join('- {}'.format(line) for line in lines))
        print()
        raise


def print_health_label_from_db(hdd_data):
    """
    A shabby version of print_health_label() using all info we have
    available in the DB.
    """
    print(
        'WARNING: total bytes read/written and total power hours '
        'not known when printing; you should have printed a health label '
        'in "dev" mode', file=sys.stderr)
    print('... but printing a partial label for you anyway.', file=sys.stderr)

    health = hdd_data['current_health']['status'].upper()
    author_of_health = hdd_data['current_health']['extra_info'].strip()
    if '--' in author_of_health:
        author_of_health = author_of_health.rsplit('--', 1)[-1]
    else:
        author_of_health = 'unknown'
    serial = hdd_data['serial_number']
    date_of_health = hdd_data['current_health']['timestamp'].split('T')[0]

    lines = [
        f'Health status : {health} @ {date_of_health}',
        '',
        f'Serial : {serial}',
        'Total bytes written/read : (not known in db)',
        'Power on hours : (not known in db)',
        f'--{author_of_health} @ {date_of_health}',
    ]
    try:
        labelprinter_rest_client = get_labelprinter()
        labelprinter_rest_client.print_generic_label(lines)
    except Exception:
        print('Would have printed:')
        print('\n'.join('- {}'.format(line) for line in lines))
        print()
        raise


def build_hdd_info(hdd_dock):
    hwdata = hdd_dock.hwdata

    static_data = []

    static_data.append(['Device model', hdd_dock.get_device_model()])
    static_data.append(['Serial', hdd_dock.get_serial_number()])
    static_data.append(
        ['Device (port)', '{} ({})'.format(
            hdd_dock.devname, hdd_dock.port if hdd_dock.port else 'Unknown')])
    static_data.append(['SSD', ('yes' if hdd_dock.is_ssd() else 'no')])
    static_data.append(
        ['SAS (detected)', ('yes' if hdd_dock.is_sas() else 'no')])
    static_data.append(['User Capacity', hdd_dock.get_user_capacity()])

    dynamic_data = []

    total_bytes_written = S_UNSET
    total_bytes_read = S_UNSET
    if hwdata.sector_size is not None:
        if hwdata.lbas_written is not None:
            total_bytes_written = human_readable_bytes(
                hwdata.sector_size * hwdata.lbas_written)
        if hwdata.lbas_read is not None:
            total_bytes_read = human_readable_bytes(
                hwdata.sector_size * hwdata.lbas_read)
    dynamic_data.append(['Total bytes written', total_bytes_written])
    dynamic_data.append(['Total bytes read', total_bytes_read])

    def _NS(value):
        if value is None:
            return S_UNSET
        return str(value)

    dynamic_data.append([
        'Power on hours',
        '{} hours'.format(_NS(hwdata.power_on_hours))])
    dynamic_data.append([
        'Wear health percent', '{}% (smart: {})'.format(
            _NS(hwdata.wear_health_percent), hwdata.smart_status)])
    dynamic_data.append([
        'Reallocated sector count',
        _NS(hwdata.reallocated_sector_ct)])
    dynamic_data.append([
        'Reallocated event count',
        _NS(hwdata.reallocated_event_count)])
    dynamic_data.append([
        'Current pending sector',
        _NS(hwdata.current_pending_sector)])
    dynamic_data.append([
        'Offline uncorrectable',
        _NS(hwdata.offline_uncorrectable)])

    return static_data, dynamic_data


def dev_menu(devname):
    author = os.environ.get('EMAIL', '')
    if '@' not in author:
        print('ERROR: Please set the EMAIL envvar to specify who you are!')
        exit(1)
    location = os.environ.get('LOCATION', 'remote')
    if not location:
        print('ERROR: Please (un)set the LOCATION envvar to specify where!')
        exit(1)

    hdd_dock = BaseStorageDevice.from_devname(devname)
    sys.stdout.write('\x1b]2;DOCKTOOL DISK BAY: {}\x07'.format(
        hdd_dock.docktool_bay_nr))

    # XXX: build_hdd_info() is a quick hack..
    static_data, dynamic_data = build_hdd_info(hdd_dock)

    inventory_rest_client = InventoryRESTClient(
        settings.DASHBOARD_BASE_URL)

    # HDD is an asset so asset_id = hdd_id
    try:
        hdd_id = inventory_rest_client.get_hdd_id(
            hdd_dock.get_device_model(),
            hdd_dock.get_serial_number())
    except ValueError as e:
        warn(str(e))
        do_print(static_data + dynamic_data, hdd_dock)
        raise

    print(
        '\n\x1b[1mBEWARE:\x1b[0m All your actions will be recorded '
        'as performed by: \x1b[1;32m{}\x1b[0m\n'
        'Change EMAIL envvar if it is incorrect!'.format(author))
    print(
        '\x1b[1mBEWARE:\x1b[0m LOCATION is set to: \x1b[1;32m{}\x1b[0m\n'
        'Change to "OSSO HQ: HDD docktool" if in the office.\n'
        .format(location))

    if hdd_id is None:
        do_print(static_data + dynamic_data, hdd_dock)
        register_disk(
            hdd_dock=hdd_dock,
            inventory_rest_client=inventory_rest_client,
            author=author, location=location)
        hdd_id = inventory_rest_client.get_hdd_id(
            hdd_dock.get_device_model(),
            hdd_dock.get_serial_number())
        assert hdd_id, 'HDD id not set after registration?'
    else:
        registered_disk_actions(
            hdd_dock=hdd_dock, hdd_id=hdd_id,
            inventory_rest_client=inventory_rest_client,
            static_data=static_data, dynamic_data=dynamic_data,
            author=author, location=location)


def db_menu(serial):
    inventory_rest_client = InventoryRESTClient(
        settings.DASHBOARD_BASE_URL)

    # HDD is an asset so asset_id = hdd_id
    hdd_id = inventory_rest_client.get_hdd_id(None, serial)  # serial?
    if hdd_id is not None:
        hdd = inventory_rest_client.get_hdd(hdd_id)[0]
    else:
        hdd = inventory_rest_client.get_hdd(serial)[0]  # hdd_id as "serial"
    if hdd is None:
        raise ValueError('serial/asset not found in remote DB')

    # Ok, we have an ID. Get info from remote?
    do_print_health_label = None
    while do_print_health_label not in ('y', 'n', 'Y', 'N', ''):
        do_print_health_label = raw_input('Print health label? (y/N): ')

    if do_print_health_label:
        print_health_label_from_db(hdd)
        print('done.')
    else:
        from pprint import pprint
        pprint(hdd)


class DocktoolArgumentParser(argparse.ArgumentParser):
    def __init__(self):
        super().__init__(
            prog='osso-docktool',
            description='Docktool for processing disks')  # exit_on_error=False

        subparser = self.add_subparsers(
            help='sub-command help',
            parser_class=argparse.ArgumentParser)
        devparser = subparser.add_parser(
            'dev',
            help='(implied!) process hardware device (original behaviour)')
        dbparser = subparser.add_parser(
            'db', help='process devices device info without hardware access')

        devparser.add_argument(
            'device', metavar='DISK', type=self.block_device,
            help='Device to use for example: /dev/sda')
        dbparser.add_argument(
            'serial', metavar='SERIAL',
            help='Serial number (or GoCollect asset UID')
        self.message2 = None

    def parse_args(self):
        if len(sys.argv) == 2 and not sys.argv[1].startswith('-'):
            sys.argv[1:1] = ['dev']  # imply "dev"
        return super().parse_args()

    def exit(self, status=0, message=None):
        if self.message2:
            print('{prog}: {message}'.format(
                prog=self.prog, message=self.message2),
                file=sys.stderr)
            self.message2 = None
        elif len(sys.argv) == 1:
            try:
                candidates = sorted(set([
                    os.path.realpath(os.path.join('/dev/disk/by-id', i))
                    for i in os.listdir('/dev/disk/by-id')]))
            except FileNotFoundError:
                # ??? no /dev/disk/by-id?
                candidates = ['(no disks found?)']
            message2 = 'suggesting disks:{}'.format(
                '\n  '.join([''] + candidates))
            print('{prog}: {message}'.format(
                prog=self.prog, message=message2),
                file=sys.stderr)

        super().exit(status=0, message=message)

    def block_device(self, name):
        try:
            st = os.stat(name)
        except FileNotFoundError:
            if '/' not in name:
                ret = self.block_device('/dev/{}'.format(name))
                warn('Prepended /dev/ to the block device name')
                return ret
            self.message2 = '{!r}: not found'.format(name)
            raise argparse.ArgumentError('{}: not found'.format(name))
        if not stat.S_ISBLK(st.st_mode):
            self.message2 = '{!r}: not a block device'.format(name)
            raise argparse.ArgumentError('{}: not a block device'.format(name))
        if os.getuid() != 0:
            warn('Expected UID 0 (root) for access')
        return name


def main():
    parser = DocktoolArgumentParser()
    args = parser.parse_args()

    try:
        if hasattr(args, 'device'):
            dev_menu(args.device)
        elif hasattr(args, 'serial'):
            db_menu(args.serial)
        else:
            assert len(sys.argv) == 1, sys.argv  # only for the no arg case
            print(
                'osso-docktool: error: invalid arguments, see --help',
                file=sys.stderr)
            sys.exit(1)
    except Exception as e:
        print('ERROR: {}\n'.format(e), file=sys.stderr)
        print()
        print(traceback.format_exc(), file=sys.stderr)
        raw_input('Error found, please inform developer. Press enter')
        # #raise e  # (a bit duplicate, no?)
        exit(1)


if __name__ == '__main__':
    main()
