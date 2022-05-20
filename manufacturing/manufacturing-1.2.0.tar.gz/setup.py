# -*- coding: utf-8 -*-
from setuptools import setup

packages = \
['manufacturing']

package_data = \
{'': ['*']}

install_requires = \
['matplotlib>=3.5.1,<4.0.0',
 'openpyxl>=3.0.9,<4.0.0',
 'pandas>=1.4.2,<2.0.0',
 'scipy>=1.7.0,<2.0.0',
 'xlrd>=2.0.1,<3.0.0']

setup_kwargs = {
    'name': 'manufacturing',
    'version': '1.2.0',
    'description': 'Six-Sigma based analysis of manufacturing data',
    'long_description': '# Purpose\n\nTo provide analysis tools and metrics useful in manufacturing environments.\n\nGo to the [documentation](https://slightlynybbled.github.io/manufacturing/index.html).\n\n# Project Maturity\n\nProject is currently undergoing frequent updates for documentation and to add\nfunctionality and update documentation!!  Screenshots and features that you see\non here may be out of date, but are in progress.\n\nCurrent focus is to add more plot types.\n\n# Installation\n\nTo install from `pypi`:\n\n    pip install manufacturing\n\nTo install from source download and install using poetry:\n\n    poetry install\n\n# Usage\n\n## Cpk Visualization\n\nThe most useful feature of the `manufacturing` package is the visualization of Cpk.\nAs hinted previously, the `ppk_plot()` function is the primary method for display of\nCpk visual information.  First, get your data into a `list`, `numpy.array`, or \n`pandas.Series`; then supply that data, along with the `lower_control_limit` and \n`upper_control_limit` into the `ppk_plot()` function.\n\n    manufacturing.ppk_plot(data, lower_specification_limit=-2, upper_specification_limit=2)\n    \n![Screenshot](images/example3.png)\n\nIn this example, it appears that the manufacturing processes are not up to the task of \nmaking consistent product within the specified limits.\n\n## Zone Control Visualization\n\nAnother useful feature is the zone control visualization.\n\n    manufacturing.control_chart(data)\n\nThere are X-MR charts, Xbar-R charts, and Xbar-S charts available as well.  If you call the \n`control_chart()` function, the appropriate sample size will be selected and data grouped as\nthe dataset requires.  However, if you wish to call a specific type of control chart, use\n\n - `x_mr_chart`\n - `xbar_r_chart`\n - `xbar_s_chart`\n - `p_chart`\n\n# Contributions\n\nContributions are welcome!  \n\n## RoadMap\n\nItems marked out were added most recently.\n\n - ...\n - ~~Add use github actions for deployment~~\n - ~~Transition to `poetry` for releases~~\n - ~~Add `I-MR Chart` (see `examples/imr_chart.py`)~~\n - ~~Add `Xbar-R Chart` (subgroups between 2 and 10)~~\n - ~~Add `Xbar-S Chart` (subgroups of 11 or more)~~\n - ~~Update documentation to reflect recent API changes~~\n - ~~Add `p chart`~~\n - Add `np chart`\n - Add `u chart`\n - Add `c chart`\n - Add automated testing (partially implemented)\n\n# Gallery\n\n![Ppk example](docs/_static/images/ppk_plot.png)\n\n![Cpk example](docs/_static/images/cpk_plot.png)\n\n![X-MR Chart](docs/_static/images/xmr_chart.png)\n\n![Xbar-R Chart](docs/_static/images/xbarr_chart.png)\n\n![Xbar-S Chart](docs/_static/images/xbars_chart.png)\n',
    'author': 'Jason R. Jones',
    'author_email': 'slightlynybbled@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
