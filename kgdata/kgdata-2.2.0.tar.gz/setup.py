# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['kgdata',
 'kgdata.dbpedia',
 'kgdata.misc',
 'kgdata.wikidata',
 'kgdata.wikidata.datasets',
 'kgdata.wikidata.deprecated',
 'kgdata.wikidata.deprecated.models',
 'kgdata.wikidata.models',
 'kgdata.wikipedia',
 'kgdata.wikipedia.datasets',
 'kgdata.wikipedia.models']

package_data = \
{'': ['*']}

install_requires = \
['beautifulsoup4>=4.9.3,<5.0.0',
 'chardet>=4.0.0,<5.0.0',
 'cityhash>=0.2.3,<0.3.0',
 'click>=8.1.3,<9.0.0',
 'fastnumbers>=3.1.0,<4.0.0',
 'hugedict>=1.4.0,<2.0.0',
 'lbry-rocksdb-optimized>=0.8.1,<0.9.0',
 'loguru>=0.6.0',
 'numpy>=1.22.3,<2.0.0',
 'orjson>=3.6.8,<4.0.0',
 'parsimonious>=0.8.1,<0.9.0',
 'pyspark==3.0.3',
 'rdflib>=6.1.1,<7.0.0',
 'redis>=3.5.3,<4.0.0',
 'requests>=2.27.1,<3.0.0',
 'ruamel.yaml>=0.17.9,<0.18.0',
 'sem-desc>=3.4.2,<4.0.0',
 'six>=1.16.0,<2.0.0',
 'tqdm>=4.64.0,<5.0.0',
 'ujson>=5.1.0,<6.0.0']

entry_points = \
{'console_scripts': ['kgdata = kgdata.__main__:cli']}

setup_kwargs = {
    'name': 'kgdata',
    'version': '2.2.0',
    'description': 'Library to process dumps of knowledge graphs (Wikipedia, DBpedia, Wikidata)',
    'long_description': 'KGData is a library to process dumps of Wikipedia, Wikidata and DBPedia.\n\n![PyPI](https://img.shields.io/pypi/v/kgdata)\n\n## Contents\n\n<!--ts-->\n\n- [Usage](#usage)\n  - [Wikidata](#wikidata)\n  - [Wikipedia](#wikipedia)\n- [Installation](#installation)\n<!--te-->\n\n## Usage\n\n### Wikidata\n\n```\nUsage: python -m kgdata.wikidata [OPTIONS] COMMAND [ARGS]...\n\nOptions:\n  --help  Show this message and exit.\n\nCommands:\n  classes              Wikidata classes\n  entities             Wikidata entities\n  entity_labels        Wikidata entity labels\n  entity_redirections  Wikidata entity redirections\n  properties           Wikidata properties\n  wp2wd                Mapping from Wikipedia articles to Wikidata entities\n```\n\nYou need the following dumps:\n\n1. entity dump ([`latest-all.json.bz2`](https://dumps.wikimedia.org/wikidatawiki/entities/20200518/wikidata-20200518-all.json.bz2)): needed to extract entities, classes and properties.\n2. `wikidatawiki-page.sql.gz` and `wikidatawiki-redirect.sql.gz` ([link](https://dumps.wikimedia.org/wikidatawiki)): needed to extract redirections of old entities.\n\nThen, execute the following steps:\n\n1.  Download the wikidata dumps (e.g., [`latest-all.json.bz2`](https://dumps.wikimedia.org/wikidatawiki/entities/20200518/wikidata-20200518-all.json.bz2)) and put it to `<wikidata_dir>/step_0` folder.\n1.  Extract entities, entity Labels, and entity redirections:\n    - `kgdata wikidata entities -d <wikidata_dir> -o <database_directory> -c`\n    - `kgdata wikidata entity_labels -d <wikidata_dir> -o <database_directory> -c`\n    - `kgdata wikidata entity_redirections -d <wikidata_dir> -o <database_directory> -c`\n1.  Extract ontology:\n    - `kgdata wikidata classes -d <wikidata_dir> -o <database_directory> -c`\n    - `kgdata wikidata properties -d <wikidata_dir> -o <database_directory> -c`\n\nFor more commands, see `scripts/build.sh`.\nIf compaction step (compact rocksdb) takes lots of time, you can run without `-c` flag.\nIf you run directly from source, replacing the `kgdata` command with `python -m kgdata`.\n\nWe provide functions to read the databases built from the previous step and return a dictionary-like objects in the module: [`kgdata.wikidata.db`](/kgdata/wikidata/db.py). In the same folder, you can find models of Wikidata [entities](/kgdata/wikidata/models/qnode.py), [classes](/kgdata/wikidata/models/wdclass.py), and [properties](/kgdata/wikidata/models/wdproperty.py).\n\n### Wikipedia\n\nHere is a list of dumps that you need to download depending on the database/files you want to build:\n\n1. [Static HTML Dumps](https://dumps.wikimedia.org/other/enterprise_html/): they only dumps some namespaces. The namespace that you likely to use is 0 (main articles). For example, enwiki-NS0-20220420-ENTERPRISE-HTML.json.tar.gz.\n\nThen, execute the following steps:\n\n1. Extract HTML Dumps:\n   - `kgdata wikipedia -d <wikipedia_dir> enterprise_html_dumps`\n\n## Installation\n\n### From pip\n\nYou need to have gcc in order to install `cityhash`\n\n```bash\npip install kgdata\n```\n\n### From Source\n\nThis library uses Apache Spark 3.0.3 (`pyspark` version is `3.0.3`). If you use different Spark version, make sure that version of `pyspark` package is matched (in `pyproject.toml`).\n\n```bash\npoetry install\nmkdir dist; zip -r kgdata.zip kgdata; mv kgdata.zip dist/ # package the application to submit to Spark cluster\n```\n\nYou can also consult the [Dockerfile](./Dockerfile) for guidance to install from scratch.\n',
    'author': 'Binh Vu',
    'author_email': 'binh@toan2.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/binh-vu/kgdata',
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'entry_points': entry_points,
    'python_requires': '>=3.8,<4.0',
}


setup(**setup_kwargs)
