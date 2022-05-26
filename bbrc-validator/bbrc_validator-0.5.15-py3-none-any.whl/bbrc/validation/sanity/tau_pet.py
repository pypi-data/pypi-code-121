from ..test import ExperimentTest, ScanTest, Results
from ..utils import __is_valid_scan__
from . import pet


class IsScannerVersionCorrect(pet.IsScannerVersionCorrect):

    passing = 'BBRCDEV_E02957',
    failing = 'BBRCDEV_E02948',
    scanner_info = {'Manufacturer': ['SIEMENS'],
                    'ManufacturersModelName': ['Biograph64', 'Biograph64_mCT'],
                    'SoftwareVersion(s)': ['VG62B']}
    __doc__ = pet.IsScannerVersionCorrect.__doc__
    __doc__ = __doc__.replace(
        pet.IsScannerVersionCorrect.scanner_info['SoftwareVersion(s)'][0],
        scanner_info['SoftwareVersion(s)'][0])


class HasUsableT1(pet.HasUsableT1):
    passing = 'BBRCDEV_E02957',
    failing = 'BBRCDEV_E02948',
    included_projects = ['testenv', 'ALFA_PLUS', 'ALFA_PLUS2', 'ALFA_OPCIONAL',
                         'ALFA_PLUS_V2', 'ALFA_PLUS2_V2', 'EPAD', 'ALFA_PLUS_VX']
    __doc__ = pet.HasUsableT1.__doc__


class IsInjectionTimeConsistent(pet.IsInjectionTimeConsistent):
    passing = 'BBRCDEV_E02957',
    failing = 'BBRCDEV_E02948',
    injection_times = {'t807': 80}

    __doc__ = pet.IsInjectionTimeConsistent.__doc__
    __doc__ = __doc__.replace(
        'Flutemetamol PET: 90 min ± 20%; Fluorodeoxyglucose PET: 45 min ± 20%',
        'TAU PET: 80 min ± 20%')
