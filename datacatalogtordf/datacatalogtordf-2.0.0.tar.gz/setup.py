# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['datacatalogtordf']

package_data = \
{'': ['*']}

install_requires = \
['concepttordf>=2.0.0,<3.0.0',
 'rdflib>=6.1.1,<7.0.0',
 'skolemizer>=1.1.0,<2.0.0']

setup_kwargs = {
    'name': 'datacatalogtordf',
    'version': '2.0.0',
    'description': 'A library for mapping a data catalog to rdf',
    'long_description': '# datacatalogtordf\n\n![Tests](https://github.com/Informasjonsforvaltning/datacatalogtordf/workflows/Tests/badge.svg)\n[![codecov](https://codecov.io/gh/Informasjonsforvaltning/datacatalogtordf/branch/master/graph/badge.svg)](https://codecov.io/gh/Informasjonsforvaltning/datacatalogtordf)\n[![PyPI](https://img.shields.io/pypi/v/datacatalogtordf.svg)](https://pypi.org/project/datacatalogtordf/)\n[![Read the Docs](https://readthedocs.org/projects/datacatalogtordf/badge/)](https://datacatalogtordf.readthedocs.io/)\n\nA small Python library for mapping a data catalog to rdf\n\nThe library contains helper classes for the following dcat classes:\n\n- [Catalog](https://www.w3.org/TR/vocab-dcat-2/#Class:Catalog)\n- [Dataset](https://www.w3.org/TR/vocab-dcat-2/#Class:Dataset)\n- [Distribution](https://www.w3.org/TR/vocab-dcat-2/#Class:Distribution)\n- [Data Service](https://www.w3.org/TR/vocab-dcat-2/#Class:Data_Service)\n\n Other relevant classes are also supported, such as:\n\n- Contact [vcard:Kind](https://www.w3.org/TR/2014/NOTE-vcard-rdf-20140522/#d4e1819)\n\n The library will map to [the Norwegian Application Profile](https://doc.difi.no/dcat-ap-no/) of [the DCAT standard](https://www.w3.org/TR/vocab-dcat-2/).\n\n## Usage\n\n### Install\n\n```Shell\n% pip install datacatalogtordf\n```\n\n### Getting started\n\n```Python\nfrom datacatalogtordf import Catalog, Dataset\n\n# Create catalog object\ncatalog = Catalog()\ncatalog.identifier = "http://example.com/catalogs/1"\ncatalog.title = {"en": "A dataset catalog"}\ncatalog.publisher = "https://example.com/publishers/1"\n\n# Create a dataset:\ndataset = Dataset()\ndataset.identifier = "http://example.com/datasets/1"\ndataset.title = {"nb": "inntektsAPI", "en": "incomeAPI"}\n#\n# Add dataset to catalog:\ncatalog.datasets.append(dataset)\n\n# get rdf representation in turtle (default)\nrdf = catalog.to_rdf()\nprint(rdf)\n```\n\n## Development\n\n### Requirements\n\n- [pyenv](https://github.com/pyenv/pyenv) (recommended)\n- python3\n- [pipx](https://github.com/pipxproject/pipx) (recommended)\n- [poetry](https://python-poetry.org/)\n- [nox](https://nox.thea.codes/en/stable/)\n\n```Shell\n% pipx install poetry==1.1.13\n% pipx install nox==2022.1.7\n% pipx inject nox nox-poetry==0.9.0\n```\n\n### Install developer tools\n\n```Shell\n% git clone https://github.com/Informasjonsforvaltning/datacatalogtordf.git\n% cd datacatalogtordf\n% pyenv install 3.8.12\n% pyenv install 3.9.10\n% pyenv local 3.8.12 3.9.10 \n% poetry install\n```\n\n### Run all sessions\n\n```Shell\n% nox\n```\n\n### Run all tests with coverage reporting\n\n```Shell\n% nox -rs tests\n```\n\n### Debugging\n\nYou can enter into [Pdb](https://docs.python.org/3/library/pdb.html) by passing `--pdb` to pytest:\n\n```Shell\nnox -rs tests -- --pdb\n```\n\nYou can set breakpoints directly in code by using the function `breakpoint()`.\n',
    'author': 'Stig B. Dørmænen',
    'author_email': 'stigbd@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://github.com/Informasjonsforvaltning/datacatalogtordf',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.10',
}


setup(**setup_kwargs)
