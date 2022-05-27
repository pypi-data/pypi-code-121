from __future__ import print_function

from warnings import warn
import os.path
import re
import subprocess

from .devtype import DEVTYPE_NVME

__author__ = 'osso'


def _assert_int(value):
    "Precondition or postcondition to check that this is an int"
    assert isinstance(value, int), value
    return value


class NvmeDataError(Exception):
    pass


class NvmeDataParser(object):
    devtype = DEVTYPE_NVME

    def __init__(self, devname):
        self.devname = devname
        # Yes, nvme cli has --output-format=json too, but it lacks explanation
        # of which fields are what, and there is no guarantee that it won't
        # change either (and string fields are right-padded):
        # -H = --human-readable
        self.rawdata = (
            self._get_nvme_data(['id-ctrl', '-H']) + '\n' +
            self._get_nvme_data(['id-ns', '-H']) + '\n' +
            self._get_nvme_data(['smart-log']))
        self.information, self.attributes = (
            self._parse_nvme_information(self.rawdata))

    def _get_nvme_data(self, cmd):
        nvmecli = '/usr/sbin/nvme'
        try:
            p = subprocess.Popen(
                [nvmecli] + cmd + [self.devname],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
        except FileNotFoundError as e:
            raise NvmeDataError('{} is not installed'.format(
                nvmecli)) from e

        # Some devices return junk as part of the vendor name.
        stdout = stdout.decode('utf-8', 'ignore')
        stderr = stderr.decode('utf-8', 'ignore')

        if p.returncode != 0:
            raise NvmeDataError('nvme cli error {} on {}: {}'.format(
                p.returncode, self.devname, (
                    stderr + '\n\n' + stdout).strip()))

        return stdout

    @property
    def device_model(self):
        """
        mn : INTEL SSDPE2KX010T8
        """
        return self.information['mn']

    @property
    def model_family(self):
        """
        ???
        """
        return None

    @property
    def serial_number(self):
        """
        sn : BTLM1170116EDJ94GK
        """
        return self.information['sn']

    @property
    def user_capacity(self):
        """
        nvmcap  : 1000204886016 <-- from 'id-ns'
        """
        # Caller expects string
        if self.information['nvmcap']:
            return str(self.information['nvmcap'])
        elif self.information['nsze']:
            return str(self.information['nsze'] * self.sector_size)
        raise NotImplementedError()

    @property
    def firmware_version(self):
        """
        fr : VDV10131
        """
        return self.information['fr']

    @property
    def ata_version(self):
        """
        ???
        """
        return 'unknown'

    @property
    def smart_status(self):
        """
        Must be enabled, since we didn't die on the 'smart-log' cmd..
        """
        assert isinstance(self.information['critical_warning'], int), (
            self.information['critical_warning'])
        if self.information['critical_warning']:
            return 'FAILED!'
        return 'PASSED'

    @property
    def sector_size(self):
        """
        LBA Format  0 : Metadata Size: 0   bytes - Data Size: 512 bytes -
          Relative Performance: 0x2 Good (in use)
        LBA Format  1 : Metadata Size: 0   bytes - Data Size: 4096 bytes -
          Relative Performance: 0 Best

        or, in json:

        "flbas" : 0  # "Formatted LBA Size" (current)
        "nlbaf" : 1  # 0-based count of sizeof(lbafs)
        "lbafs" : [
          {"ms" : 0, "ds" : 9, "rp" : 2},  # 9=512
          {"ms" : 0, "ds" : 12, "rp" : 0}  # 12=4096
        ]
        """
        if not hasattr(self, '_sector_size'):
            for key, value in self.information.items():
                if key.startswith('LBA Format ') and '(in use)' in value:
                    for line in value.split(' - '):
                        if line.startswith('Data Size'):
                            self._sector_size = int(
                                line.split(':', 1)[1].strip().split(' ', 1)[0])
                            return self._sector_size
                    return ValueError('Parse error of sector_size {!r}'.format(
                        value))
            return ValueError('Cannot find LBA Format in information')
        return self._sector_size

    @property
    def wear_health_percent(self):
        """
        Returns estimated health of device (from 100 down to 0 (or below))
        """
        # We want a value that represents the health, like the
        # wear_leveling_count did. Returns a signed integer from 100
        # and downwards. (May become negative.)
        used_health = int(self.information['percentage_used'].replace('%', ''))
        return 100 - used_health

    @property
    def power_on_hours(self):
        return _assert_int(self.information['power_on_hours'])

    @property
    def lbas_read(self):
        return _assert_int(self.information['host_read_commands'])

    @property
    def lbas_written(self):
        return _assert_int(self.information['host_write_commands'])

    @property
    def reallocated_sector_ct(self):
        return None  # ??? perhaps something with available_spare(_threshold)

    @property
    def reallocated_event_count(self):
        return None  # ??? see above

    @property
    def current_pending_sector(self):
        return None

    @property
    def offline_uncorrectable(self):
        return None

    def _parse_nvme_information(self, rawdata):
        it = iter(rawdata.split('\n'))

        # frmw      : 0x2
        #   [4:4] : 0   Firmware Activate Without Reset Not Supported
        #   [3:1] : 0x1	Number of Firmware Slots
        #   [0:0] : 0   Firmware Slot 1 Read/Write
        # ...
        #   [31:1] : 0x6a\tReserved
        bitre = re.compile(r'\s*\[(\d+):(\d+)\]\s*:\s*([0-9a-fx]+)\s+(.*)$')

        information = {}
        last_key = None

        for line in it:
            indent = line.startswith(' ')
            try:
                key, value = line.split(':', 1)
            except ValueError:
                # No ':' found.. ignore.
                pass
            else:
                key = key.strip()

                if key.startswith('['):
                    # [31:30] : 0x2 Blah <-- bits 30+31 have 31 set
                    self._populate_subinfo(
                        information, key, value, last_key, line, bitre)
                elif not indent:
                    last_key = key
                    self._populate_info(information, key, value)

        attributes = {}
        if not attributes:
            warn('No attributes found')

        return information, attributes

    def _populate_info(self, information, key, value):
        # "frmw      : 0x2" => {"frmw": 0x02}
        value = value.strip()
        if value.startswith('0x') or value == '0':
            value = int(value, 16)  # 0x12 -> 18
        elif all(group.isdigit() for group in value.split(',')) and (
                all(len(group) == 3 for group in value.split(',')[1:])):
            value = int(value.replace(',', ''))  # 1,234,567 -> 1234567
        if key not in information:
            information[key] = value
        else:
            assert False, ((key, value), information)

    def _populate_subinfo(self, information, key, value, last_key, line,
                          bitre):
        assert last_key  # must be something
        # > [31:30] : 0x2 Blah <-- bits 30+31 have 31 set
        # " [31:30] : 0x2 Blah" => {"frmw:30:31": 0x2}
        m = bitre.match(line)
        assert m, (
            'does not match bitre: {}'.format(bitre.pattern), line)
        bitend, bitstart, value, name = m.groups()
        if bitend == bitstart:
            value = bool(int(value, 16))    # 0, 0x1
            information['{}:{}'.format(last_key, bitend)] = value
        else:
            value = int(value, 16)          # 0, 0x1, 0x2, ...
            information['{}:{}:{}'.format(
                last_key, bitend, bitstart)] = value


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print('Usage {} device'.format(
            os.path.basename(sys.argv[0])), file=sys.stderr)
        sys.exit(1)

    # (in smart-log)
    # critical_warning                    : 0
    # temperature                         : 34 C
    # available_spare                     : 100%
    # available_spare_threshold           : 10%
    # percentage_used                     : 0%
    # data_units_read                     : 37
    # data_units_written                  : 0
    # host_read_commands                  : 1056
    # host_write_commands                 : 0
    # controller_busy_time                : 0
    # power_cycles                        : 4
    # power_on_hours                      : 912
    # unsafe_shutdowns                    : 2
    # media_errors                        : 0
    # num_err_log_entries                 : 0
    # Warning Temperature Time            : 0
    # Critical Composite Temperature Time : 0
    # Thermal Management T1 Trans Count   : 0
    # Thermal Management T2 Trans Count   : 0
    # Thermal Management T1 Total Time    : 0
    # Thermal Management T2 Total Time    : 0

    parser = NvmeDataParser(sys.argv[1])
    for prop in (
            'device_model',
            'model_family',
            'serial_number',
            'user_capacity',
            'firmware_version',
            'ata_version',
            'smart_status',
            'sector_size',
            'lbas_written',
            'lbas_read',
            'power_on_hours',
            'wear_health_percent',
            'reallocated_sector_ct',
            'reallocated_event_count',
            'current_pending_sector',
            'offline_uncorrectable'):
        val = getattr(parser, prop)
        str_val = str(val) if val is not None else '(N/A)'
        print('{:24}: {}'.format(prop, str_val))
