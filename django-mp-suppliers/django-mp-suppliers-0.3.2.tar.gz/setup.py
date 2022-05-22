
from setuptools import setup, find_packages


version = '0.3.2'
url = 'https://github.com/pmaigutyak/mp-suppliers'

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name='django-mp-suppliers',
    version=version,
    description='Django suppliers app',
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='{}/archive/{}.tar.gz'.format(url, version),
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=requires
)
