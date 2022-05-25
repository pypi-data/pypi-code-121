from setuptools import setup, find_packages
import os

VERSION = '0.0.1'
DESCRIPTION = 'Add folders to path for a virtual environment'
with open(os.path.join(os.path.dirname(__file__), 'README.rst'), encoding='utf8') as f: 
    LONG_DESCRIPTION = f.read()

setup(
    name='virtualenv-update-path',
    version=VERSION,
    author='Sindre Osnes',
    author_email='sindreosnes.git@gmail.com',
    url="https://github.com/SindreOsnes/virtualenv-update-path",
    packages=find_packages(exclude=['test']),
    description=DESCRIPTION,
    long_description=LONG_DESCRIPTION,
    entry_points={
        'console_scripts': [
            'virtualenv-update-path=virtualenv_update_path.runners:update_path'
        ]
    },
    install_requires=[
    ],
    test_suite='test',
    python_requires='>=3.7'
)