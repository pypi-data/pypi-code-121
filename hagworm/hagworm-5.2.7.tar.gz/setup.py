# -*- coding: utf-8 -*-

__author__ = r'wsb310@gmail.com'

import ssl
import setuptools

from hagworm import __version__


ssl._create_default_https_context = ssl._create_unverified_context

with open(r'README.md', encoding=r'utf8') as stream:
    long_description = stream.read()

setuptools.setup(
    name=r'hagworm',
    version=__version__,
    license=r'Apache License Version 2.0',
    platforms=[r'all'],
    author=r'Shaobo.Wang',
    author_email=r'wsb310@gmail.com',
    description=r'Network Development Suite',
    long_description=long_description,
    long_description_content_type=r'text/markdown',
    url=r'https://gitee.com/wsb310/hagworm',
    packages=setuptools.find_packages(),
    package_data={r'hagworm': [r'static/*.*']},
    python_requires=r'>= 3.8',
    install_requires=[
        r'APScheduler==3.9.1',
        r'Pillow==9.0.1',
        r'PyJWT==2.3.0',
        r'PyYAML==6.0',
        r'SQLAlchemy==1.3.24',
        r'aiohttp==3.8.1',
        r'aiomysql==0.1.1',
        r'aioredis==1.3.1',
        r'aioredis-cluster==1.7.1',
        r'aiosmtplib==1.1.6',
        r'aliyun-log-python-sdk==0.7.9',
        r'cachetools==5.0.0',
        r'cryptography==37.0.2',
        r'fastapi==0.76.0',
        r'fastapi-health==0.4.0',
        r'gunicorn==20.1.0',
        r'hiredis==2.0.0',
        r'httptools==0.4.0',
        r'loguru==0.6.0',
        r'motor==3.0.0',
        r'mq-http-sdk==1.0.3',
        r'msgpack==1.0.3',
        r'ntplib==0.4.0',
        r'numpy==1.22.3',
        r'psutil==5.9.0',
        r'pyahocorasick==1.4.4',
        r'pytest-asyncio==0.18.3',
        r'python-stdnum==1.17',
        r'python-multipart==0.0.5',
        r'pyzmq==22.3.0',
        r'qrcode==7.3.1',
        r'terminal-table==2.0.1',
        r'ujson==5.2.0',
        r'uvicorn==0.17.6',
        r'uvloop==0.16.0;sys_platform!="win32"',
        r'xmltodict==0.13.0',
    ],
    classifiers=[
        r'Programming Language :: Python :: 3.8',
        r'License :: OSI Approved :: Apache Software License',
        r'Operating System :: POSIX :: Linux',
    ],
    ext_modules=[
        setuptools.Extension(
            r'hagworm.extend.math', [r'./c_extend/math.c']
        ),
    ],
)
