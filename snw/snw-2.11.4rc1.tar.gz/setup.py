from setuptools import setup

setup(
    name='snw',
    version='2.11.4rc1',
    description='snw client tool',
    author='Jean Senellart',
    author_email='jean.senellart@systrangroup.com',
    url='http://www.systransoft.com',
    scripts=['client/snw'],
    package_dir={'client': 'nmt-wizard/client', 'lib': 'client/lib', 'srx': 'corpus-acquisition/pyscripts'},
    packages=['client', 'lib', 'lib.commands', 'srx'],
    install_requires=[
        'python-pcre',
        'configparser',
        'enlighten',
        'prettytable',
        'requests',
        'six>=1.14.0',
        'setuptools',
        'jsonschema',
        'packaging>=17.0',
        'semver'
    ]
)
