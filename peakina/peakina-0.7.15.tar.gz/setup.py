# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['peakina',
 'peakina.io',
 'peakina.io.ftp',
 'peakina.io.http',
 'peakina.io.local',
 'peakina.io.s3',
 'peakina.readers']

package_data = \
{'': ['*']}

install_requires = \
['certifi>=2021.10.8,<2022.0.0',
 'chardet>=4.0.0,<5.0.0',
 'fastparquet>=0.8.0,<0.9.0',
 'jq>=1.2.1,<2.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas==1.2.5',
 'paramiko>=2.9.2,<3.0.0',
 'pydantic>=1.9.0,<2.0.0',
 'python-slugify>=5.0.2,<7.0.0',
 'python-snappy>=0.6.0,<0.7.0',
 's3fs>=2022.1.0,<2023.0.0',
 'tables>=3.7.0,<4.0.0',
 'urllib3>=1.26.8,<2.0.0',
 'xlrd>=2.0.1,<3.0.0',
 'xmltodict>=0.12.0,<0.13.0']

setup_kwargs = {
    'name': 'peakina',
    'version': '0.7.15',
    'description': 'pandas readers on steroids (remote files, glob patterns, cache, etc.)',
    'long_description': '[![Pypi-v](https://img.shields.io/pypi/v/peakina.svg)](https://pypi.python.org/pypi/peakina)\n[![Pypi-pyversions](https://img.shields.io/pypi/pyversions/peakina.svg)](https://pypi.python.org/pypi/peakina)\n[![Pypi-l](https://img.shields.io/pypi/l/peakina.svg)](https://pypi.python.org/pypi/peakina)\n[![Pypi-wheel](https://img.shields.io/pypi/wheel/peakina.svg)](https://pypi.python.org/pypi/peakina)\n[![GitHub Actions](https://github.com/ToucanToco/peakina/workflows/CI/badge.svg)](https://github.com/ToucanToco/peakina/actions?query=workflow%3ACI)\n[![codecov](https://codecov.io/gh/ToucanToco/peakina/branch/main/graph/badge.svg)](https://codecov.io/gh/ToucanToco/peakina)\n\n# Pea Kina _aka \'Giant Panda\'_\n\nWrapper around `pandas` library, which detects separator, encoding\nand type of the file. It allows to get a group of files with a matching pattern (python or glob regex).\nIt can read both local and remote files (HTTP/HTTPS, FTP/FTPS/SFTP or S3/S3N/S3A).\n\nThe supported file types are `csv`, `excel`, `json`, `parquet` and `xml`.\n\n:information_source: If the desired type is not yet supported, feel free to open an issue or to directly open a PR with the code !\n\nPlease, read the [documentation](https://doc-peakina.toucantoco.com) for more information\n\n# Installation\n\n`pip install peakina`\n\n# Usage\nConsidering a file `file.csv`\n```\na;b\n0;0\n0;1\n```\n\nJust type\n```python\n>>> import peakina as pk\n>>> pk.read_pandas(\'file.csv\')\n   a  b\n0  0  0\n1  0  1\n```\n\nOr files on a FTPS server:\n- my_data_2015.csv\n- my_data_2016.csv\n- my_data_2017.csv\n- my_data_2018.csv\n\nYou can just type\n\n```python\n>>> pk.read_pandas(\'ftps://<path>/my_data_\\\\d{4}\\\\.csv$\', match=\'regex\', dtype={\'a\': \'str\'})\n    a   b     __filename__\n0  \'0\'  0  \'my_data_2015.csv\'\n1  \'0\'  1  \'my_data_2015.csv\'\n2  \'1\'  0  \'my_data_2016.csv\'\n3  \'1\'  1  \'my_data_2016.csv\'\n4  \'3\'  0  \'my_data_2017.csv\'\n5  \'3\'  1  \'my_data_2017.csv\'\n6  \'4\'  0  \'my_data_2018.csv\'\n7  \'4\'  1  \'my_data_2018.csv\'\n```\n\n## Using cache\n\nYou may want to keep the last result in cache, to avoid downloading and extracting the file if it didn\'t change:\n\n```python\n>>> from peakina.cache import Cache\n>>> cache = Cache.get_cache(\'memory\')  # in-memory cache\n>>> df = pk.read_pandas(\'file.csv\', expire=3600, cache=cache)\n```\n\nIn this example, the resulting dataframe will be fetched from the cache, unless `file.csv` modification time has changed on disk, or unless the cache is older than 1 hour.\n\nFor persistent caching, use: `cache = Cache.get_cache(\'hdf\', cache_dir=\'/tmp\')`\n\n\n## Use only downloading feature\n\nIf you just want to download a file, without converting it to a pandas dataframe:\n\n```python\n>>> uri = \'https://i.imgur.com/V9x88.jpg\'\n>>> f = pk.fetch(uri)\n>>> f.get_str_mtime()\n\'2012-11-04T17:27:14Z\'\n>>> with f.open() as stream:\n...     print(\'Image size:\', len(stream.read()), \'bytes\')\n...\nImage size: 60284 bytes\n```\n\n## Installation on macOS M1 chipset\n\n## install everything\n```console\nbrew install hdf5 snappy\nHDF5_DIR="/opt/homebrew/Cellar/hdf5/1.12.1/" CPPFLAGS="-I/opt/homebrew/Cellar/snappy/1.1.9/include -L/opt/homebrew/Cellar/snappy/1.1.9/lib" poetry install\n```\n\nFor more details, here is what is needed:\n\n### install pytables\n```console\nbrew install hdf5\nHDF5_DIR="/opt/homebrew/Cellar/hdf5/1.12.1/" poetry run pip install tables\n```\n\n### install python-snappy\n```console\nbrew install snappy\nCPPFLAGS="-I/opt/homebrew/Cellar/snappy/1.1.9/include -L/opt/homebrew/Cellar/snappy/1.1.9/lib" poetry run pip install python-snappy\n```\n',
    'author': 'Toucan Toco',
    'author_email': 'dev@toucantoco.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/ToucanToco/peakina',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
