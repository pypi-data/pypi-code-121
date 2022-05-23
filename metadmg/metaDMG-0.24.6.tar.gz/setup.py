# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['metaDMG',
 'metaDMG.cli',
 'metaDMG.data',
 'metaDMG.fit',
 'metaDMG.loggers',
 'metaDMG.viz',
 'metaDMG.viz.mpl_styles']

package_data = \
{'': ['*']}

install_requires = \
['PyYAML>=6.0,<7.0',
 'click-help-colors>=0.9.1,<0.10.0',
 'pandas>=1.4.1,<2.0.0',
 'pyarrow>=7.0.0,<8.0.0',
 'scipy>=1.8.0,<2.0.0',
 'typer>=0.4.0,<0.5.0']

extras_require = \
{':extra == "fit" or extra == "all"': ['logger-tt>=1.7.0,<2.0.0',
                                       'psutil>=5.9.0,<6.0.0'],
 'all': ['iminuit>=2.10.0,<3.0.0',
         'numpyro>=0.9.1,<0.10.0',
         'joblib>=1.1.0,<2.0.0',
         'numba>=0.55.1,<0.56.0',
         'matplotlib>=3.5.1,<4.0.0',
         'plotly>=5.6.0,<6.0.0',
         'dash[diskcache]>=2.3.0,<3.0.0',
         'dash-bootstrap-components>=1.0.3,<2.0.0',
         'orjson>=3.6.7,<4.0.0',
         'tqdm>=4.63.0,<5.0.0'],
 'fit': ['iminuit>=2.10.0,<3.0.0',
         'numpyro>=0.9.1,<0.10.0',
         'joblib>=1.1.0,<2.0.0',
         'numba>=0.55.1,<0.56.0'],
 'viz': ['matplotlib>=3.5.1,<4.0.0',
         'plotly>=5.6.0,<6.0.0',
         'dash[diskcache]>=2.3.0,<3.0.0',
         'dash-bootstrap-components>=1.0.3,<2.0.0',
         'orjson>=3.6.7,<4.0.0',
         'tqdm>=4.63.0,<5.0.0']}

entry_points = \
{'console_scripts': ['metaDMG = metaDMG.cli.cli:cli_main']}

setup_kwargs = {
    'name': 'metadmg',
    'version': '0.24.6',
    'description': 'metaDMG: Estimating ancient damage in (meta)genomic DNA rapidly',
    'long_description': '![Logo](docs/source/images/logo.png)\n<!--\n```{image} docs/source/images/logo.png\n:alt: logo\n:class: bg-primary\n:width: 500px\n:align: center\n``` -->\n\n# A fast and accurate ancient DNA damage toolkit for metagenomic data\n\n[![Documentation](https://img.shields.io/badge/documentation-latest-blue.svg)](https://metadmg-dev.github.io/metaDMG-core/)\n[![Documentation](https://img.shields.io/badge/dashboard-live-blue.svg)](https://metadmg.herokuapp.com/)\n![](https://img.shields.io/pypi/v/metadmg)\n![](https://img.shields.io/pypi/pyversions/metaDMG)\n<!-- ![](https://img.shields.io/pypi/l/metaDMG) -->\n<!-- ![](https://img.shields.io/github/workflow/status/metaDMG-dev/metaDMG-core/CI-CD) -->\n<!-- ![](https://img.shields.io/pypi/dm/metaDMG) -->\n<!-- ![](https://img.shields.io/github/issues-raw/metaDMG-dev/metaDMG-core) -->\n<!-- ![](https://img.shields.io/github/issues-closed-raw/metaDMG-dev/metaDMG-core) -->\n<!-- ![](https://img.shields.io/github/languages/code-size/metaDMG-dev/metaDMG-core) -->\n\n`metaDMG` is a novel framework and suite of programs for analysing large-scale genomic data especially in the context of environmental DNA. This includes state-of-the-art statistical methods for computing nucleotide misincorporation and fragmentation patterns of even highly complex samples.\n\nFor more information, see the [documentation](https://metadmg-dev.github.io/metaDMG-core).\nFor a quick preview of the interactivity, see the [dashboard](https://metadmg.herokuapp.com).\n\n## Table of contents\n* [Getting started](#getting-started)\n* [Citing metaDMG](#citing-metadmg)\n\n## Getting Started\n\nFor information about how to get started running `metaDMG`, see the section in the [documentation](https://metadmg-dev.github.io/metaDMG-core/getting-started.html).\n\n## Citing `metaDMG`\n\nHere will be more information once our paper is released.\n',
    'author': 'Christian Michelsen',
    'author_email': 'christianmichelsen@gmail.com',
    'maintainer': 'None',
    'maintainer_email': 'None',
    'url': 'https://github.com/metaDMG/metaDMG/',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'entry_points': entry_points,
    'python_requires': '>=3.9,<3.11',
}


setup(**setup_kwargs)
