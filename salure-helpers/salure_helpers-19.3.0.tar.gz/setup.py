from setuptools import setup

setup(
    name='salure_helpers',
    version='19.3.0',
    description='Files with helpful code, developed by Salure',
    url='https://bitbucket.org/salurebi/salure_helpers/',
    author='Salure',
    author_email='bi@salure.nl',
    license='Salure License',
    packages=['salure_helpers'],
    package_data={'salure_helpers': ['templates/*', 'datasets/*', 'helpers/*']},
    install_requires=[
        'aiohttp>=3,<=4',
        'pandas>=1,<=1.35',
        'mandrill-really-maintained>=1,<=2',
        'pymysql>=1,<=2',
        'requests>=2,<=3',
        'pysftp>=0,<=1',
        'pyarrow>=0,<=6.0.1',
        'twine>=3,<=4',
        'fs>=2,<=3',
        'python-gnupg>=0,<=1',
        'xmltodict>=0,<=1',
        'zeep>=4,<=5',
        'ldap3==2.9.1',
        'azure-storage-file-share>=12.6.0'
    ],
    zip_safe=False
)
