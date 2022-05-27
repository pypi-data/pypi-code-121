import subprocess
import unittest

__author__ = 'osso'


class bool_dict(dict):
    def __str__(self):
        return '{{{}}}'.format(', '.join(
            k if v else '!{}'.format(k)
            for k, v in sorted(self.items())))


class HdparmParser(object):
    RENAME_MAP = {
        # [...] a counter in the hard disk electronics allows only five
        # attempts to enter the user password. Otherwise, the device
        # remains locked in SEC4 state. Any further attempt at unlocking
        # is only possible after a power cycle or hardware reset.
        'expired: security count': 'is_past_retry_count',
        'supported: enhanced erase': 'has_enhanced_erase',
        # The olden flags, renamed to make more sense.
        'supported': 'has_security',
        'enabled': 'is_enabled',
        'frozen': 'is_frozen',
        'locked': 'is_locked',
    }

    def __init__(self, devname):
        self._rawdata = subprocess.check_output(
            ['/sbin/hdparm', '-I', devname]).decode('utf-8')

    def get_security_info(self):
        if 'Security' not in self._rawdata:
            return None

        lines = self._rawdata.split('\n')
        security_info = {}
        do_collect = False
        for line in lines:
            if do_collect:
                if not line.startswith('\t'):
                    do_collect = False
                else:
                    splitted = line.split('\t')
                    if (len(splitted) == 3 and
                            'master password' not in splitted[1].lower()):
                        security_info[splitted[2]] = (
                            splitted[1].lower() != 'not')
            elif line.startswith('Security'):
                do_collect = True

        return bool_dict(
            (self.RENAME_MAP.get(k, k), v) for k, v in security_info.items())


class HdparmParserTestCase(unittest.TestCase):
    def test_values(self):
        class TestHdparmParser(HdparmParser):
            def __init__(self, rawdata):
                self._rawdata = rawdata

        input = '\n'.join([
            '\t   *\tREAD BUFFER DMA command'
            '\t   *\tData Set Management TRIM supported (limit 8 blocks)',
            'Security: ',
            '\tMaster password revision code = 65534',
            '\t\tsupported',
            '\tnot\tenabled',
            '\tnot\tlocked',
            '\t\tfrozen',
            '\tnot\texpired: security count',
            '\t\tsupported: enhanced erase',
            ('\t2min for SECURITY ERASE UNIT. '
             '8min for ENHANCED SECURITY ERASE UNIT.'),
            'Logical Unit WWN Device Identifier: 50025388a01c561a',
            '\tNAA\t\t: 5',
            '\tIEEE OUI\t: 002538',
        ])
        hdparamparser = TestHdparmParser(input)
        security_info = hdparamparser.get_security_info()
        self.assertEqual(security_info, {
            'is_enabled': False,
            'is_past_retry_count': False,
            'is_frozen': True,
            'is_locked': False,
            'has_security': True,
            'has_enhanced_erase': True,
        })
        self.assertEqual(str(security_info), (
            '{has_enhanced_erase, has_security, '
            '!is_enabled, is_frozen, !is_locked, !is_past_retry_count}'))
