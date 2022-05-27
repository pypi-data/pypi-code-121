# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['lightkurve',
 'lightkurve.correctors',
 'lightkurve.io',
 'lightkurve.prf',
 'lightkurve.seismology']

package_data = \
{'': ['*'], 'lightkurve': ['data/*']}

install_requires = \
['astropy>=5.0',
 'astroquery>=0.3.10',
 'beautifulsoup4>=4.6.0',
 'bokeh>=1.1',
 'fbpca>=1.0',
 'matplotlib>=3.1',
 'numpy>=1.18',
 'oktopus>=0.1.2',
 'pandas>=1.1.4',
 'patsy>=0.5.0',
 'requests>=2.22.0',
 'scikit-learn>=0.24.0',
 'tqdm>=4.25.0',
 'uncertainties>=3.1.4']

extras_require = \
{':python_version >= "3.8" and python_version < "3.11"': ['scipy>=1.7'],
 ':python_version >= "3.8" and python_version < "4.0"': ['urllib3>=1.23',
                                                         'memoization>=0.3.1']}

setup_kwargs = {
    'name': 'lightkurve',
    'version': '2.2.1',
    'description': 'A friendly package for Kepler & TESS time series analysis in Python.',
    'long_description': "Lightkurve\n==========\n\n**A friendly package for Kepler & TESS time series analysis in Python.**\n\n**Documentation: https://docs.lightkurve.org**\n\n|test-badge| |conda-badge| |pypi-badge| |pypi-downloads| |doi-badge| |astropy-badge|\n\n.. |conda-badge| image:: https://img.shields.io/conda/vn/conda-forge/lightkurve.svg\n                 :target: https://anaconda.org/conda-forge/lightkurve\n.. |pypi-badge| image:: https://img.shields.io/pypi/v/lightkurve.svg\n                :target: https://pypi.python.org/pypi/lightkurve\n.. |pypi-downloads| image:: https://pepy.tech/badge/lightkurve\n                :target: https://pepy.tech/project/lightkurve\n.. |test-badge| image:: https://github.com/lightkurve/lightkurve/workflows/Lightkurve-tests/badge.svg\n                 :target: https://github.com/lightkurve/lightkurve/actions?query=branch%3Amain\n.. |astropy-badge| image:: https://img.shields.io/badge/powered%20by-AstroPy-orange.svg?style=flat\n                   :target: http://www.astropy.org\n.. |doi-badge| image:: https://zenodo.org/badge/DOI/10.5281/zenodo.1181928.svg\n              :target: https://docs.lightkurve.org/about/citing.html             \n\n**Lightkurve** is a community-developed, open-source Python package which offers a beautiful and user-friendly way\nto analyze astronomical flux time series data,\nin particular the pixels and lightcurves obtained by\n**NASA's Kepler and TESS exoplanet missions**.\n\n.. image:: https://raw.githubusercontent.com/lightkurve/lightkurve/main/docs/source/_static/images/lightkurve-teaser.gif\n\nThis package aims to lower the barrier for students, astronomers,\nand citizen scientists interested in analyzing Kepler and TESS space telescope data.\nIt does this by providing **high-quality building blocks and tutorials**\nwhich enable both hand-tailored data analyses and advanced automated pipelines.\n\n\nDocumentation\n-------------\n\nRead the documentation at `https://docs.lightkurve.org <https://docs.lightkurve.org>`_.\n\n\nQuickstart\n----------\n\nPlease visit our quickstart guide at `https://docs.lightkurve.org/quickstart.html <https://docs.lightkurve.org/quickstart.html>`_.\n\n\nContributing\n------------\n\nWe welcome community contributions!\nPlease read the  guidelines at `https://docs.lightkurve.org/about/contributing.html <https://docs.lightkurve.org/about/contributing.html>`_.\n\n\nCiting\n------\n\nIf you find Lightkurve useful in your research, please cite it and give us a GitHub star!\nPlease read the citation instructions at `https://docs.lightkurve.org/about/citing.html <https://docs.lightkurve.org/about/citing.html>`_.\n\n\nContact\n-------\nLightkurve is an open source community project created by `the authors <AUTHORS.rst>`_.\nThe best way to contact us is to `open an issue <https://github.com/lightkurve/lightkurve/issues/new>`_ or to e-mail tesshelp@bigbang.gsfc.nasa.gov.\nPlease include a self-contained example that fully demonstrates your problem or question.\n",
    'author': 'Geert Barentsen',
    'author_email': 'hello@geert.io',
    'maintainer': None,
    'maintainer_email': None,
    'url': 'https://docs.lightkurve.org',
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'extras_require': extras_require,
    'python_requires': '>=3.8',
}


setup(**setup_kwargs)
