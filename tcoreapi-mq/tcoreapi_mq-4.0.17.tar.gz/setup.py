# -*- coding: utf-8 -*-
__author__ = 'ICE Technology'

import setuptools

setuptools.setup(
    name='tcoreapi_mq',
    version="4.0.17",
    description='tcoreapi_mq',
    author='ICE Technology',
    author_email='mcsupport@icetech.com.cn',
    url='https://voltrader.icetech.com.cn/',
    packages=setuptools.find_packages(exclude=["tcoreapi_mq.sample.*"]),
    install_requires=["pyzmq"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    include_package_data=True
)