# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['pypet2bids']

package_data = \
{'': ['*'],
 'pypet2bids': ['metadata/PET_Radionuclide.mkd',
                'metadata/PET_Radionuclide.mkd',
                'metadata/PET_Radionuclide.mkd',
                'metadata/PET_Radionuclide.mkd',
                'metadata/PET_Radionuclide.mkd',
                'metadata/PET_metadata.json',
                'metadata/PET_metadata.json',
                'metadata/PET_metadata.json',
                'metadata/PET_metadata.json',
                'metadata/PET_metadata.json',
                'metadata/blood_metadata.json',
                'metadata/blood_metadata.json',
                'metadata/blood_metadata.json',
                'metadata/blood_metadata.json',
                'metadata/blood_metadata.json',
                'metadata/definitions.json',
                'metadata/definitions.json',
                'metadata/definitions.json',
                'metadata/definitions.json',
                'metadata/definitions.json',
                'metadata/dicom2bids.json',
                'metadata/dicom2bids.json',
                'metadata/dicom2bids.json',
                'metadata/dicom2bids.json',
                'metadata/dicom2bids.json']}

install_requires = \
['json-maj>=0.0.3,<0.0.4',
 'nibabel>=3.2.1,<4.0.0',
 'numpy>=1.21.3,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.3.4,<2.0.0',
 'pydicom>=2.2.2,<3.0.0',
 'pyinstaller>=5.0,<6.0',
 'pyparsing>=3.0.4,<4.0.0',
 'pytest>=6.2.5,<7.0.0',
 'python-dateutil>=2.8.2,<3.0.0',
 'python-dotenv>=0.19.1,<0.20.0',
 'scipy>=1.7.1,<2.0.0',
 'six>=1.16.0,<2.0.0',
 'sphinx-rtd-theme>=1.0.0,<2.0.0',
 'sphinxcontrib-matlabdomain>=0.13.0,<0.14.0',
 'termcolor>=1.1.0,<2.0.0',
 'xlrd>=2.0.1,<3.0.0']

entry_points = \
{'console_scripts': ['dcm2niix4pet = pypet2bids.dcm2niix4pet:main',
                     'dcm2petbids = pypet2bids.dicom_convert:cli',
                     'ecatpet2bids = pypet2bids.ecat_cli:main',
                     'pet2bids-spreadsheet-template = '
                     'pypet2bids.helper_functions:write_out_module']}

setup_kwargs = {
    'name': 'pypet2bids',
    'version': '0.0.12',
    'description': 'A python implementation of an ECAT to BIDS converter.',
    'long_description': None,
    'author': 'anthony galassi',
    'author_email': '28850131+bendhouseart@users.noreply.github.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>3.7.1,<3.10',
}


setup(**setup_kwargs)
