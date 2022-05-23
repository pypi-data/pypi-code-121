# -*- coding: utf-8 -*-
from setuptools import setup

modules = \
['marcxml2csv']
install_requires = \
['click>=8.1.3,<9.0.0', 'lxml>=4.8.0,<5.0.0', 'tqdm>=4.64.0,<5.0.0']

entry_points = \
{'console_scripts': ['marcxml2csv = marcxml2csv:convert',
                     'picaxml2csv = picaxml2csv:convert']}

setup_kwargs = {
    'name': 'marcxml2csv',
    'version': '1.0.0',
    'description': 'A simple converter of MARCXML/PICAXML to CSV/TSV',
    'long_description': '# marcxml2csv\n\nA simple converter of (possibly gzipped) MARCXML/PICAXML to (possibly gzipped) CSV/TSV. \n\nThe resulting CSV/TSV has been designed to be easy to use as a data table, but also to retain all ordering informaation in the original when such is needed. The format is as follows:\n`record_number,field_number,subfield_number,field_code,subfield_code,value`\n\nHere, `record_number` identifies the MARC/PICA+ record, while `field_number` and `subfield_number` can be used for more exact filtering / reconstructing the original field flow if needed.\n\nFor the MARC leader and control fields, `subfield_number` will be empty.\n\nFor MARC data fields, `ind1` and `ind2` values are reported as separate rows with the `subfield_code` being `ind1` or `ind2`, but only when non-empty. The also have an empty `subfield_number`.\n\n## Installation\n\nInstall from pypi with e.g. `pipx install marcxml2csv`.\n\n## Usage\n\n```\nUsage: marcxml2csv [OPTIONS] [INPUT]...\n\n  Convert from MARCXML (gz) input files into (gzipped) CSV/TSV\n\nOptions:\n  -o, --output TEXT  Output CSV/TSV (gz) file  [required]\n  --help             Show this message and exit.\n```\n\n```\nUsage: picaxml2csv [OPTIONS] [INPUT]...\n\n  Convert from PICAXML (gz) input files into (gzipped) CSV/TSV\n\nOptions:\n  -o, --output TEXT  Output CSV/TSV (gz) file  [required]\n  --help             Show this message and exit.\n```\n\nFiles will be read/written using gzip if the filename ends with `.gz`. TSV format will be used if the output filename contains `.tsv`, otherwise CSV will be used.',
    'author': 'Eetu Mäkelä',
    'author_email': 'eetu.makela@helsinki.fi',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/hsci-r/marcxml2csv',
    'py_modules': modules,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
