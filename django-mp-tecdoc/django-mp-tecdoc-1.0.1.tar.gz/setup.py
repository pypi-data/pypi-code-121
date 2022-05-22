
from setuptools import setup, find_packages


version = '1.0.1'
url = 'https://github.com/pmaigutyak/mp-tecdoc'

with open('requirements.txt') as f:
    requires = f.read().splitlines()

setup(
    name='django-mp-tecdoc',
    version=version,
    description='Django tecdoc app',
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='{}/archive/{}.tar.gz'.format(url, version),
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=requires
)
