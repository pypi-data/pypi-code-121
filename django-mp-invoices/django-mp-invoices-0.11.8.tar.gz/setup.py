
from setuptools import setup, find_packages


with open('requirements.txt') as f:
    requires = f.read().splitlines()


version = '0.11.8'
url = 'https://github.com/pmaigutyak/mp-invoices'


setup(
    name='django-mp-invoices',
    version=version,
    description='Django invoices apps',
    author='Paul Maigutyak',
    author_email='pmaigutyak@gmail.com',
    url=url,
    download_url='%s/archive/%s.tar.gz' % (url, version),
    packages=find_packages(),
    include_package_data=True,
    license='MIT',
    install_requires=requires
)
