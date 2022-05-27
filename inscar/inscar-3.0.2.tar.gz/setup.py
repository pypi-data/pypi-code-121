# -*- coding: utf-8 -*-
from setuptools import setup

package_dir = \
{'': 'src'}

packages = \
['inscar', 'inscar.experimental']

package_data = \
{'': ['*']}

install_requires = \
['attrs>=21.4.0,<22.0.0',
 'importlib-metadata>=4.11.4,<5.0.0',
 'matplotlib>=3.4.1,<4.0.0',
 'numba>=0.55.1,<0.56.0',
 'numpy>=1.20.2,<2.0.0',
 'scipy>=1.6.2,<2.0.0']

setup_kwargs = {
    'name': 'inscar',
    'version': '3.0.2',
    'description': 'Calculate an incoherent scatter spectrum with arbitrary isotropic electron velocity distributions and radar pointing at oblique angles to the magnetic field',
    'long_description': 'inscar\n======\n\n    INcoherent SCAtter Radar spectrum\n\n|PyPI| |Status| |Python Version| |License| |Read the Docs| |Tests| |Codecov| |DOI|\n|pre-commit| |Black|\n\n.. |PyPI| image:: https://img.shields.io/pypi/v/inscar.svg\n   :target: https://pypi.org/project/inscar/\n   :alt: PyPI\n.. |Status| image:: https://img.shields.io/pypi/status/inscar.svg\n   :target: https://pypi.org/project/inscar/\n   :alt: Status\n.. |Python Version| image:: https://img.shields.io/pypi/pyversions/inscar\n   :target: https://pypi.org/project/inscar\n   :alt: Python Version\n.. |License| image:: https://img.shields.io/badge/License-MIT-yellow.svg\n   :target: https://opensource.org/licenses/MIT\n   :alt: License\n.. |Read the Docs| image:: https://img.shields.io/readthedocs/inscar/latest.svg?label=Read%20the%20Docs\n   :target: https://inscar.readthedocs.io/\n   :alt: Read the documentation at https://ncdump-rich.readthedocs.io/\n.. |Tests| image:: https://github.com/engeir/inscar/workflows/Tests/badge.svg\n   :target: https://github.com/engeir/inscar/actions?workflow=Tests\n   :alt: Tests\n.. |Codecov| image:: https://codecov.io/gh/engeir/inscar/branch/master/graph/badge.svg?token=P8S18UILSB\n   :target: https://codecov.io/gh/engeir/inscar\n   :alt: Codecov\n.. |DOI| image:: https://zenodo.org/badge/233043566.svg\n   :target: https://zenodo.org/badge/latestdoi/233043566\n   :alt: pre-commit\n.. |pre-commit| image:: https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit&logoColor=white\n   :target: https://github.com/pre-commit/pre-commit\n   :alt: pre-commit\n.. |Black| image:: https://img.shields.io/badge/code%20style-black-000000.svg\n   :target: https://github.com/psf/black\n   :alt: Black\n\n.. [![release](https://img.shields.io/github/release/engeir/inscar.svg)](https://github.com/engeir/inscar/releases/latest)\n.. ![CodeQL](https://github.com/engeir/inscar/workflows/CodeQL/badge.svg)\n\n.. image:: ./img/normal_is_spectra.png\n\nInfo\n----\n\nCalculates an incoherent scatter radar spectrum based on the theory presented in\n`Hagfors (1961)`_ and `Mace (2003)`_.\n\nInstalling\n----------\n\nYou can install *inscar* via pip_ from PyPI_:\n\n.. code:: console\n\n   $ pip install inscar\n\nUsage\n-----\n\nPlease see the `Modules Reference <Modules_>`_ for details.\n\nNumba\n^^^^^\n\nFaster integration is accomplished by computing in parallel. This is\naccomplished using `numba`.\n\nPhysical environment\n^^^^^^^^^^^^^^^^^^^^\n\nThe available plasma parameters that can be changed within the program are\n\n.. code:: text\n\n    === Input parameters ===\n    K_RADAR -- Radar wavenumber (= -4pi(radar frequency)/(speed of light)) [m^(-1)]\n    B -- Magnetic field strength [T]\n    MI -- Ion mass in atomic mass units [u]\n    NE -- Electron number density [m^(-3)]\n    NU_E -- Electron collision frequency [Hz]\n    NU_I -- Ion collision frequency [Hz]\n    T_E -- Electron temperature [K]\n    T_I -- Ion temperature [K]\n    T_ES -- Temperature of suprathermal electrons in the gauss_shell VDF [K] (no longer in use)\n    THETA -- Aspect angle [1]\n    Z -- Height used for calculated distribution [100, 599] [km]\n    mat_file -- Time of day for calculated distribution\n    pitch_angle -- Pitch angle for calculated distribution\n\nCalculation method\n^^^^^^^^^^^^^^^^^^\n\nThe program support different methods of calculating the spectrum, based on how you\nassume the particles to be distributed. This includes a Maxwellian distribution and a\nkappa distribution, in addition to any arbitrary isotropic distribution.\n\n.. _Hagfors (1961): https://agupubs.onlinelibrary.wiley.com/doi/epdf/10.1029/JZ066i006p01699\n.. _Mace (2003): https://aip.scitation.org/doi/pdf/10.1063/1.1570828\n.. _PyPI: https://pypi.org/\n.. _pip: https://pip.pypa.io/\n.. github-only\n.. _Contributor Guide: CONTRIBUTING.rst\n.. _Modules: https://inscar.readthedocs.io/en/latest/modules.html\n',
    'author': 'engeir',
    'author_email': 'eirroleng@gmail.com',
    'maintainer': None,
    'maintainer_email': None,
    'url': None,
    'package_dir': package_dir,
    'packages': packages,
    'package_data': package_data,
    'install_requires': install_requires,
    'python_requires': '>=3.8,<3.11',
}


setup(**setup_kwargs)
