from __future__ import print_function

from warnings import warn
import os.path
import re
import subprocess

from .devtype import DEVTYPE_HDD, DEVTYPE_NVME, DEVTYPE_SSD

__author__ = 'osso'


class SmartDataError(Exception):
    pass


class SmartDataParser(object):
    def __init__(self, devname):
        self.devname = devname
        self.rawdata = self._get_smart_data()
        self.information, self.attributes = (
            self._parse_smart_information(self.rawdata))
        self.devtype = self._get_devtype()

    def _get_devtype(self):
        if 'NVMe' in self.rawdata:
            devtype = DEVTYPE_NVME
        elif 'solid state' in self.information.get(
                'Rotation Rate', '').lower():
            devtype = DEVTYPE_SSD
        else:
            devtype = DEVTYPE_HDD
        return devtype

    def _get_smart_data(self):
        smartctl = '/usr/sbin/smartctl'
        try:
            p = subprocess.Popen(
                [smartctl, '-x', self.devname],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            stdout, stderr = p.communicate()
        except FileNotFoundError as e:
            raise SmartDataError('{} is not installed'.format(
                smartctl)) from e

        # Some devices return junk as part of the vendor name.
        stdout = stdout.decode('utf-8', 'ignore')
        stderr = stderr.decode('utf-8', 'ignore')

        if p.returncode & (
                0x1 |  # "Command line did not parse"
                0x2):  # "Device open failed or ..."
            raise SmartDataError('smartctl error {} on {}: {}'.format(
                p.returncode, self.devname, (
                    stderr + '\n\n' + stdout).strip()))

        return stdout

    @property
    def device_model(self):
        """
        Device Model: Samsung SSD 850 PRO 256GB
        """
        information = self.information
        if 'Model Number' in information:
            return information['Model Number']
        if 'Device Model' in information:
            return information['Device Model']
        if 'Product' in information:
            return information['Product']
        raise ValueError('no modelname found in {}'.format(information))

    @property
    def model_family(self):
        """
        Model Family: Samsung based SSDs
        """
        if 'Model Family' in self.information:
            return self.information['Model Family']
        return None

    @property
    def serial_number(self):
        """
        Serial Number: S1SUNSAF81L482Z
        """
        information = self.information
        key_options = [
            x for x in information.keys() if x.lower() == 'serial number']
        if len(key_options) == 1:
            return information[key_options[0]]
        raise Exception(
            'Serial number could not be determined from info: {0}'.format(
                information))

    @property
    def user_capacity(self):
        """
        User Capacity: 256,060,514,304 bytes [256 GB]
        """
        information = self.information
        if 'User Capacity' in information:
            return information['User Capacity']
        if 'Total NVM Capacity' in information:
            return information['Total NVM Capacity']
        if 'Namespace 1 Size/Capacity' in information:
            return information['Namespace 1 Size/Capacity']
        raise Exception(
            'User capacity could not be determined from info: {0}'.format(
                information))

    @property
    def firmware_version(self):
        """
        Firmware Version: EXM01B6Q
        """
        return self.information.get('Firmware Version', 'unknown')

    @property
    def ata_version(self):
        """
        ATA Version is: ACS-2, ATA8-ACS T13/1699-D revision 4c
        """
        return self.information.get('ATA Version is', 'unknown')

    @property
    def smart_status(self):
        """
        SMART support is: Available - device has SMART capability.
        SMART support is: Enabled  <-- 2nd one is kept!
        SMART overall-health self-assessment test result: PASSED
        """
        if self.information.get('SMART support is') != 'Enabled':
            print('WARNING: SMART support not enabled? {!r} + {!r}'.format(
                self.information.get('SMART support is'),
                self.information.get('SMART overall-health')))
            return 'MISSING'
        elif not self.information.get('SMART overall-health'):
            print('WARNING: SMART not passed?')
            return 'Enabled'
        return self.information.get('SMART overall-health')

    @property
    def sector_size(self):
        """
        Sector Size: 512 bytes logical/physical
        """
        match = re.match(r'([0-9]*) ', self.information.get('Sector Size', ''))
        if match:
            return int(match.groups()[0])
        # Default to 512 (bytes)
        return 512

    def _get_value(self, search_str, column_name):
        data = [
            x for x in self.attributes
            if x.get('attribute_name', '').lower() == search_str]

        if data:
            value = data[0].get(column_name, None)
            try:
                value = int(value)
            except ValueError:
                pass
            return value
        return None

    @property
    def wear_health_percent(self):
        """
        Returns estimated health of device (from 100 down to 0 (or below))
        """
        # This is a percentage (the value, that is), which goes down from 100%
        # to 0% (= no health); taken from the obscurely named
        # "wear_leveling_count".
        keys = ('media_wearout_indicator', 'wear_leveling_count')
        for key in keys:
            wear = self._get_value(key, 'value')
            if wear is not None:
                break
        else:
            if self.devtype == DEVTYPE_HDD:
                # Spinners have no wearout indication.
                wear = 100  # 100% ok == "OK".. unless we have any other info..
            else:
                raise ValueError(
                    'no wear attribute found for {} (type {!r}), '
                    'please file bug'.format(self.device_model, self.devtype))
        return int(wear)

    @property
    def power_on_hours(self):
        return self._get_value('power_on_hours', 'raw_value')

    @property
    def lbas_read(self):
        return self._get_value('total_lbas_read', 'raw_value')

    @property
    def lbas_written(self):
        return self._get_value('total_lbas_written', 'raw_value')

    @property
    def reallocated_sector_ct(self):
        return self._get_value('reallocated_sector_ct', 'raw_value')

    @property
    def reallocated_event_count(self):
        return self._get_value('reallocated_event_count', 'raw_value')

    @property
    def current_pending_sector(self):
        return self._get_value('current_pending_sector', 'raw_value')

    @property
    def offline_uncorrectable(self):
        return self._get_value('offline_uncorrectable', 'raw_value')

    def _parse_smart_information(self, rawdata):
        it = iter(rawdata.split('\n'))

        information = {}
        for line in it:
            if 'START OF INFORMATION SECTION' in line:
                break
        # === START OF INFORMATION SECTION ===
        # Model Family:     Samsung based SSDs
        # Device Model:     Samsung SSD 840 EVO 120GB
        for line in it:
            line = line.strip()
            if not line:
                break
            if ':' not in line:
                warn('smartctl line without KEY/VALUE: {}'.format(line))
            else:
                key, value = line.split(':', 1)
                key = key.strip()
                if key != 'SMART support is':
                    assert key not in information, ((key, value), information)
                value = value.strip()
                information[key] = value
        assert information, 'No info found in smart data:\n{}'.format(
            rawdata)

        attributes = []
        for line in it:
            # === START OF READ SMART DATA SECTION ===
            # SMART overall-health self-assessment test result: PASSED
            # SMART overall-health self-assessment test result: FAILED!
            if line.startswith('SMART overall-health self-assessment') and (
                    ':' in line):
                information['SMART overall-health'] = (
                    line.split(':', 1)[1].strip())
            elif line.startswith('SMART Health Status:'):
                # SAS disk, Seagate ST10000NM0226
                information['SMART overall-health'] = (
                    line.split(':', 1)[1].strip())

            # ID# ATTRIBUTE_NAME  FLAGS  VALUE ...
            elif 'ID# ATTRIBUTE_NAME' in line:
                attribute_headers = [
                    i.lower() for i in re.split(r' +', line)]
                break
        # ID# ATTRIBUTE_NAME          FLAGS    VALUE WORST THRESH FAIL RAW_VAL
        #   5 Reallocated_Sector_Ct   PO--CK   100   100   010    -    0
        #   9 Power_On_Hours          -O--CK   080   080   000    -    99644
        #  12 Power_Cycle_Count       -O--CK   099   099   000    -    44
        # 177 Wear_Leveling_Count     PO--C-   082   082   000    -    216
        for line in it:
            line = line.strip()
            split = re.split(r' +', line)
            if '|' in split[0]:  # ||||| pointing to the FLAGS
                break
            values = {}
            for nr, key in enumerate(attribute_headers):
                values[key] = split[nr]
            attributes.append(values)

        if not attributes:
            warn('smartctl: No attributes found')

        return information, attributes


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print('Usage {} device'.format(
            os.path.basename(sys.argv[0])), file=sys.stderr)
        sys.exit(1)

    # ID# ATTRIBUTE_NAME          FLAGS  VALUE WORST THRESH FAIL RAW_VALUE
    #   5 Reallocated_Sector_Ct   PO--CK 100   100   010    -    0
    #   9 Power_On_Hours          -O--CK 084   084   000    -    76546
    #  12 Power_Cycle_Count       -O--CK 099   099   000    -    22
    # 177 Wear_Leveling_Count     PO--C- 076   076   000    -    1452
    # 179 Used_Rsvd_Blk_Cnt_Tot   PO--C- 100   100   010    -    0
    # 181 Program_Fail_Cnt_Total  -O--CK 100   100   010    -    0
    # 182 Erase_Fail_Count_Total  -O--CK 100   100   010    -    0
    # 183 Runtime_Bad_Block       PO--C- 100   100   010    -    0
    # 187 Uncorrectable_Error_Cnt -O--CK 100   100   000    -    0
    # 190 Airflow_Temperature_Cel -O--CK 069   037   000    -    31
    # 195 ECC_Error_Rate          -O-RC- 200   200   000    -    0
    # 199 CRC_Error_Count         -OSRCK 100   100   000    -    0
    # 235 POR_Recovery_Count      -O--C- 099   099   000    -    8
    # 241 Total_LBAs_Written      -O--CK 099   099   000    -    167448209929

    parser = SmartDataParser(sys.argv[1])
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
