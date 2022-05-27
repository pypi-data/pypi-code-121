import os
import re
import subprocess
import time

from . import settings
from .devtype import DEVTYPE_HDD, DEVTYPE_NVME, DEVTYPE_SSD
from .nvmedata import NvmeDataError, NvmeDataParser
from .smartdata import SmartDataError, SmartDataParser
from .hdparm import HdparmParser

__author__ = 'osso'


class UnmatchedStorageDevice(Exception):
    pass


class BaseStorageDevice(object):
    @classmethod
    def from_devname(cls, devname):
        for class_ in (
                NvmeStorageDevice,
                SgSanitizeStorageDevice,
                FallbackStorageDevice,
                ):
            try:
                devtype, hwdata = class_._get_hwdata(devname)
            except UnmatchedStorageDevice as e:
                last_exception = e
            else:
                return class_(devname, devtype, hwdata)
        raise last_exception

    @classmethod
    def _get_hwdata(cls, devname):
        raise NotImplementedError()

    def __init__(self, devname, devtype, hwdata):
        self.devname = devname
        self.devtype = devtype
        self.hwdata = hwdata
        self.status = 'Initialized'
        self.port = self._get_port()
        self.docktool_bay_nr = self._get_docktool_bay_nr(self.port)

    def flush(self):
        self.devtype, self.hwdata = self._get_hwdata(self.devname)

    def get_device_model(self):
        # "Samsung SSD 850 PRO 256GB" or ValueError
        return self.hwdata.device_model

    def get_model_family(self):
        # "Samsung based SSDs" or None
        return self.hwdata.model_family

    def get_serial_number(self):
        # "S1SUNSAF81L482Z" or ValueError
        return self.hwdata.serial_number

    def get_user_capacity(self):
        # "256,060,514,304 bytes [256 GB]" or None
        return self.hwdata.user_capacity

    def get_firmware_version(self):
        # "EXM01B6Q" or "unknown"
        return self.hwdata.firmware_version

    def get_ata_version(self):
        # "ACS-2, ATA8-ACS T13/1699-D revision 4c" or "unknown"
        return self.hwdata.ata_version

    def get_smart_status(self):
        # "PASSED" or "OK" or "FAILED!" or "Enabled" or "MISSING"
        return self.hwdata.smart_status

    def is_sas(self):
        return 'sas' in self.hwdata.information.get(
            'Transport protocol', '').lower()

    def is_ssd(self):
        return (self.devtype in (DEVTYPE_NVME, DEVTYPE_SSD))

    def _get_docktool_bay_nr(self, port):
        return settings.ATA_TO_BAY_NR.get(port, None)

    def _get_port(self):
        realpath = os.path.realpath(self.devname)
        bypath = '/dev/disk/by-path/'
        found_symlinks = []
        for symlink in os.listdir(bypath):
            if os.path.realpath(os.path.join(bypath, symlink)) == realpath:
                found_symlinks.append(symlink)
        port = None
        if found_symlinks:
            assert len(found_symlinks) == 1
            for regex in [
                    # 'pci-0000:00:1f.2-ata-1'
                    r'-(ata-\d+)',
                    # 'pci-0000:17:00.0-nvme-1'
                    r'(^pci-.*nvme-\d+)',
                    # 'pci-0000:19:00.0-sas-e..f-phy5-lun-0'
                    r'-(phy\d+)',
                    # 'pci-0000:00:14.0-usb-0:13.2:1.0-scsi-0:0:0:0'
                    r'-(usb-\d+)']:
                match = re.search(regex, found_symlinks[0])
                if match:
                    port = match.groups()[0]
                    break

        return port or self.devname

    def get_erase_methods(self):
        return [self.wipe_using_manual_methods]

    def wipe_using_manual_methods(self):
        """
        Wipe using modified urandom stream + zerofill.

        Slow.
        """
        if not settings.DEBUG:
            # secure erase by using /dev/urandom
            subprocess.check_output([
                '/usr/local/bin/run-lessrandom', self.devname])
            subprocess.check_output([
               '/usr/local/bin/run-zero-disk', self.devname])
            self.status = 'Secure erased'
        else:
            print('WARNING: Skipping manual erase because DEBUG')

        return True, None
    wipe_using_manual_methods.name = 'manual, slow'
    wipe_using_manual_methods.type = 'manual'  # manual = slow

    def quick_erase(self):
        if not settings.DEBUG:
            # Quick erase by zeroing begin and end of disk:
            # - 160M at the start
            startbs, startcount = (1024 * 1024), 160
            # - 104M at the end
            endbs, endcount = 512, 204800

            with open(self.devname, 'rb') as fp:
                size = fp.seek(0, 2)

            subprocess.check_output([
                'dd',
                'if=/dev/zero',
                'of={}'.format(self.devname),
                'bs={}'.format(startbs),
                'seek=0',
                'count={}'.format(startcount),
                'conv=fsync'])
            subprocess.check_output([
                'dd',
                'if=/dev/zero',
                'of={}'.format(self.devname),
                'bs={}'.format(endbs),
                'count={}'.format(endcount),
                'seek={}'.format((size // endbs) - endcount),
                'conv=fsync'])
        else:
            print('WARNING: Skipping quick erase because DEBUG')

        self.status = 'Quick erased'

    def shutdown_disk(self):
        print('\nSpinning down/ejecting disk, please wait...\n')
        if settings.DEBUG:
            print('WARNING: Skipping spindown/eject because DEBUG')
        elif self.is_sas():
            subprocess.check_output([
                '/usr/bin/sdparm', '--readonly', '--command=stop',
                self.devname])
        elif self.devtype == DEVTYPE_NVME:
            print('WARNING: No idea how to eject and NVMe dev; needed?')
        else:
            assert self.devtype in (DEVTYPE_HDD, DEVTYPE_SSD)
            # FIXME: what if we don't want to spin it down? because we're not
            # ejecting it
            subprocess.check_output(['/sbin/hdparm', '-Y', self.devname])
        self.status = 'Shutdown'


class GenericStorageDeviceBase(BaseStorageDevice):
    @classmethod
    def _get_hwdata(cls, devname):
        try:
            hwdata = SmartDataParser(devname)
        except SmartDataError as e:
            raise UnmatchedStorageDevice(e) from e
        if hwdata.devtype == DEVTYPE_NVME:
            raise NotImplementedError(
                'programming error; we should be in NvmeStorageDevice')
        return hwdata.devtype, hwdata


class SgSanitizeStorageDevice(GenericStorageDeviceBase):
    @classmethod
    def _get_hwdata(cls, devname):
        devtype, hwdata = super()._get_hwdata(devname)

        # Is this as SAS disk, then assume hdparm security yields None
        # and we might get crypto erase support.
        if 'sas' in hwdata.information.get('Transport protocol', '').lower():
            # Assert that a SAS disk does not do hdparm stuff.
            hdparm_sec_info = HdparmParser(devname).get_security_info()
            assert hdparm_sec_info is None, (
                hdparm_sec_info, hwdata.information)

            # Try sg_opcodes.
            opcodes = cls._get_sg_security_info(devname)
            if opcodes['sanitize_crypto_erase']:
                return devtype, hwdata

        raise UnmatchedStorageDevice()

    def get_erase_methods(self):
        return [
            self.wipe_using_sanitize_crypto_erase,
            self.wipe_using_manual_methods]

    def wipe_using_sanitize_crypto_erase(self):
        # /usr/bin/sg_sanitize --quick --wait --verbose --crypto devname
        if not settings.DEBUG:
            if not (
                    self._get_sg_security_info(self.devname)
                    ['sanitize_crypto_erase']):
                return False, 'no sanitize_crypto_erase available'
            subprocess.check_call([
                '/usr/bin/sg_sanitize', '--quick', '--wait', '--verbose',
                '--crypto', self.devname])
            return True, None
        else:
            print('WARNING: Skipping crypto erase erase because DEBUG')
            return True, None
    wipe_using_sanitize_crypto_erase.name = 'sanitize crypto erase'
    wipe_using_sanitize_crypto_erase.type = 'builtin'  # fast!

    @classmethod
    def _get_sg_security_info(cls, devname):
        opcodes = cls._get_sg_opcodes(devname)
        ret = {
            # 'sanitize_overwrite': False,
            'sanitize_crypto_erase': False,
        }
        if (0x48, '1') in opcodes:
            # This, is no fun. I tested one Seagate 10TB disk, and it did
            # 175MB/s for the first 3.78% (in 36 minutes). That translates to
            # 16 hours for the total disk.
            # # sg_requests /dev/sda
            # > Decode parameter data as sense data:
            # > Fixed format, current; Sense key: Not Ready
            # > Additional sense: Logical unit not ready, sanitize in progress
            # >   Progress indication: 3.78%
            # Additionally, it might even have stalled now, as the status
            # update from sg_requests totally hung at t0+4hours.
            # #ret['sanitize_overwrite'] = True
            pass
        if (0x48, '3') in opcodes:
            ret['sanitize_crypto_erase'] = True
        return ret

    @classmethod
    def _get_sg_opcodes(cls, devname):
        # > # sg_opcodes --compact /dev/sda
        # >   SEAGATE   ST10000NM0226     KT01
        # >   Peripheral device type: disk
        # >
        # > Opcode,sa  Name
        # >   (hex)
        # > ---------------------------------------
        # >  00        Test Unit Ready
        # >  01        Rezero Unit
        # >  03        Request Sense
        # > ...
        # >  48,1      Sanitize, overwrite
        # >  48,3      Sanitize, cryptographic erase
        # >  48,1f     Sanitize, exit failure mode
        opcodes = (
            subprocess.check_output(
                ['/usr/bin/sg_opcodes', '--compact', devname])
            .decode('utf-8'))
        it = iter(opcodes.strip().split('\n'))
        for line in it:
            if line.startswith('----'):
                break
        ret = {}
        for line in it:
            opcode, title = line.strip().split(None, 1)
            opcodes = opcode.split(',')
            opcodes[0] = int(opcodes[0], 16)
            assert tuple(opcodes) not in ret, (ret, opcodes)
            ret[tuple(opcodes)] = title
        return ret


class FallbackStorageDevice(GenericStorageDeviceBase):
    def get_erase_methods(self):
        if self._can_secure_erase()[0]:
            return [
                self.wipe_using_security_erase, self.wipe_using_manual_methods]
        return [self.wipe_using_manual_methods]

    def _can_secure_erase(self):
        security_info = HdparmParser(self.devname).get_security_info()
        if security_info is None:
            return False, 'no hdparm security, no sg_opcode security'

        for x in ['has_security', 'is_enabled', 'is_locked', 'is_frozen']:
            if x not in security_info:
                return False, '{} not found in security_info: {}'.format(
                    x, security_info)

        if not security_info['has_security']:
            return False, 'Block device secure erase seems not to be supported'

        if security_info['is_enabled']:
            assert False, (
                'Block device password for secure erase is already set')

        if security_info['is_locked']:
            assert False, (
                'Block device is locked (try replugging the disk or '
                'hibernating system)')

        if security_info['is_frozen']:
            assert False, (
                'Block device is frozen (try replugging the disk or '
                'hibernating system)')

        if security_info.get('is_past_retry_count'):
            assert False, (
                'Block device is past password retry count (time to look up '
                'a master password?)')

        return True, None

    def wipe_using_security_erase(self):
        # $1 = /dev/sdc
        # secret=`pwgen -s 32 1`
        # hdparm --user-master u --security-set-pass $secret $1
        # hdparm --user-master u --security-erase $secret $1
        if not settings.DEBUG:
            can_erase, error = self._can_secure_erase()
            if not can_erase:
                return False, error
            return self._wipe_using_hdparm_security_erase()
        else:
            print('WARNING: Skipping secure erase because DEBUG')
            return True, None
    wipe_using_security_erase.name = 'secure SSD/HDD erase'
    wipe_using_security_erase.type = 'builtin'  # slow? fast?

    def _wipe_using_hdparm_security_erase(self):
        # Create secret
        # XXX: this is problematic if the system dies before we've called
        # security-erase: afterwards the disk sometimes stays locked. It'd
        # be nicer if we wiped with a pre-existing pw?
        secret = subprocess.check_output([
            '/usr/bin/pwgen', '-s', '32', '1'])[0:32].decode('utf-8')

        # Set the password. This should set is_enabled ('enabled')
        # in hdparm security info.
        print('WARNING: The hdparm --security-set-pass sometimes says: ')
        print('  "SG_IO: bad/missing sense data, sb[]:  70 00 01 00 ..."')
        print('This might be ignorable. Please inform developer.')
        print(
            'NOTICE: Using secret {!r}.. you may need this to unbrick!'
            .format(secret))

        print('> --security-set-pass')
        subprocess.check_output([
            '/sbin/hdparm', '--user-master', 'u',
            '--security-set-pass', secret, self.devname])

        # Check hdparm security info. Only perform secure BLKDEV
        # erase if security is indeed enabedl.
        security_info = HdparmParser(self.devname).get_security_info()
        print('> {}'.format(security_info))
        if not security_info.get('is_enabled'):
            return False, (
                'Block device password could not be set, '
                'security info: {}'.format(security_info))

        for i in range(10):
            # Try secure erase.
            if security_info.get('has_enhanced_erase', False):
                print('> --security-erase-enhanced')
                subprocess.check_output([
                    '/sbin/hdparm', '--user-master', 'u',
                    '--security-erase-enhanced', secret, self.devname])
            else:
                print('> --security-erase')
                subprocess.check_output([
                    '/sbin/hdparm', '--user-master', 'u',
                    '--security-erase', secret, self.devname])
            # Check that hdparm security is now unset.
            security_info = HdparmParser(self.devname).get_security_info()
            print('> {}'.format(security_info))
            if not security_info.get('is_enabled', True):
                break
            # This could be a problem.. retry this a few times..
            print(
                'WARNING: Security erase/unset failed (password {!r});'
                'retrying in 3..'.format(secret))
            time.sleep(3)
        else:
            return False, (
                'Block device password could not be UNset, '
                'security info: {}, secret: {!r}'.format(
                    security_info, secret))

        return True, None


class NvmeStorageDevice(BaseStorageDevice):
    @classmethod
    def _get_hwdata(cls, devname):
        try:
            hwdata = NvmeDataParser(devname)
        except NvmeDataError as e:
            raise UnmatchedStorageDevice(e) from e
        assert hwdata.devtype == DEVTYPE_NVME, hwdata.devtype
        return hwdata.devtype, hwdata

    def get_erase_methods(self):
        methods = []
        flags = self._get_secure_erase_options()

        # We prefer:
        # - nvme-sanitize (wipes data AND cache)
        #     over
        # - nvme-format (wipes data).
        # We prefer:
        # - crypto-erase
        #     over
        # - no-secure-erase

        # However: the block erase is a lot slower than crypto erase..
        # What to do, what to do?
        if flags['can_crypto_sanitize']:
            methods.append(self.wipe_using_crypto_sanitize)  # fast
        if flags['can_block_sanitize']:
            methods.append(self.wipe_using_block_sanitize)  # slow
        if flags['can_crypto_erase']:
            methods.append(self.wipe_using_crypto_erase)  # fast
        if flags['can_format']:
            methods.append(self.wipe_using_block_erase)  # fast
        methods.append(self.wipe_using_manual_methods)
        return methods

    def wipe_using_block_erase(self):
        if not settings.DEBUG:
            subprocess.check_output(
                ['/usr/sbin/nvme', 'format', self.devname, '--ses=1'])
        else:
            print('WARNING: Skipping secure block erase because DEBUG')
        return True, None
    wipe_using_block_erase.name = 'nvme format (poor)'
    wipe_using_block_erase.type = 'builtin'  # ???

    def wipe_using_block_sanitize(self):
        if not settings.DEBUG:
            subprocess.check_output(
                ['/usr/sbin/nvme', 'sanitize', self.devname, '--sanact=0x2'])
        else:
            print('WARNING: Skipping secure block sanitize because DEBUG')
        return True, None
    wipe_using_block_sanitize.name = 'nvme block sanitize (better)'
    wipe_using_block_sanitize.type = 'builtin'  # ???

    def wipe_using_crypto_erase(self):
        if not settings.DEBUG:
            subprocess.check_output(
                ['/usr/sbin/nvme', 'format', self.devname, '--ses=2'])
        else:
            print('WARNING: Skipping secure crypto erase because DEBUG')
        return True, None
    wipe_using_crypto_erase.name = 'nvme crypto erase (better)'
    wipe_using_crypto_erase.type = 'builtin'  # ???

    def wipe_using_crypto_sanitize(self):
        if not settings.DEBUG:
            subprocess.check_output(
                ['/usr/sbin/nvme', 'sanitize', self.devname, '--sanact=0x4'])
        else:
            print('WARNING: Skipping secure crypto sanitize because DEBUG')
        return True, None
    wipe_using_crypto_sanitize.name = 'nvme crypto sanitize (best)'
    wipe_using_crypto_sanitize.type = 'builtin'  # ???

    def _get_secure_erase_options(self):
        if self.devtype != DEVTYPE_NVME:
            return False, 'Disk was not recognized as NVMe Device'

        # > Secure erase is faster, but not as complete. Data on a drive that
        # > has been securely erased or sanitized cannot be recovered. If power
        # > is interrupted during a secure erase, secure erase may continue as
        # > soon as power is restored or the user may need to issue another
        # > secure erase command when power is restored. Note that SSD
        # > manufacturers do not follow a universal command to sanitize drives.

        # "Format NVM Supported"
        can_format = False
        if self.hwdata.information['oacs:1']:  # 2nd bit of oacs
            assert bool(self.hwdata.information['oacs'] & 0x2)  # same info
            can_format = True
            # -> nvme format /dev/nvme0 --ses=1  # nvme format/wipe

        # "Crypto Erase Supported as part of Secure Erase"
        can_crypto_erase = False
        if can_format and self.hwdata.information['fna:2']:
            assert bool(self.hwdata.information['fna'] & 0x4)  # same info
            can_crypto_erase = True
            # -> nvme format /dev/nvme0 --ses=2  # nvme crypto format

        # "Block Erase Sanitize Operation (Not) Supported"
        can_block_sanitize = False
        # "Crypto Erase Sanitize Operation (Not) Supported"
        can_crypto_sanitize = False
        if self.hwdata.information['sanicap']:
            if self.hwdata.information['sanicap:1']:
                assert bool(self.hwdata.information['sanicap'] & 0x2)  # same
                can_block_sanitize = True
                # # 010b - Start a Block Erase sanitize operation
                # # 011b - Start an Overwrite sanitize operation
                # # 100b - Start a Crypto Erase sanitize operation
                # -> nvme sanitize /dev/nvme0 --sanact=0x2  # block sanitize
            if self.hwdata.information['sanicap:0']:
                assert bool(self.hwdata.information['sanicap'] & 0x1)  # same
                can_crypto_sanitize = True
                # # 010b - Start a Block Erase sanitize operation
                # # 011b - Start an Overwrite sanitize operation
                # # 100b - Start a Crypto Erase sanitize operation
                # -> nvme sanitize /dev/nvme0 --sanact=0x4  # crypto sanitize

        # can_crypto_erase = True && can_crypto_sanitize = False
        # --> means quick erase (but not best)
        # --> or slow erase (crypto sanitize)
        return {
            'can_crypto_sanitize': can_crypto_sanitize,
            'can_crypto_erase': can_crypto_erase,
            'can_block_sanitize': can_block_sanitize,
            'can_format': can_format,
        }
