from setuptools import setup, find_packages

from opentsdb import __version__


setup(
    name='opentsdb-client',
    version=__version__,
    author='Okeyja Teung',
    author_email='dengyijian163@163.com',
    packages=find_packages(),
    keywords="opentsdb, tsdb, metrics",
    url='https://github.com/neilbowman666/opentsdb-client',
    download_url='https://github.com/neilbowman666/opentsdb-client/archive/v{VERSION}.zip'.format(VERSION=__version__),
    description='Python3 client for OpenTSDB',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Natural Language :: English',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3 :: Only'
    ],
    install_requires=[
        "setuptools",
        "requests"
    ]
)
