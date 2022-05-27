from setuptools import setup

__version__ = '0.0.12'

install_requires = \
['pandas>=1.3.5',
 'pyreadr>=0.4.4',
 'requests>=2.26.0',
 'wget>=3.2,<4.0',
 'wbgapi >= 1.0.7'
 ]

setup(
    name='arg-econ-data',
    version=__version__,
    packages=['arg_econ_data'],
    include_package_data=True,
    install_requires=install_requires,
)