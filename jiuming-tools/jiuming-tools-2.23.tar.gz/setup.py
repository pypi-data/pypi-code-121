# -*- coding:utf-8 -*-
from setuptools import setup, find_packages

from src.config.global_config import get_version

setup(
    name='jiuming-tools',
    # 版本 如果需要发布更新 需要调整版本号
    version=get_version(),
    packages=find_packages(),
    include_package_data=True,
    # data_files=[
    #     # 打包打进ming.yaml
    #     ('', ['ming.yaml'])
    # ],
    platforms='linux',
    # 需要的依赖
    install_requires=[
        'Click==7.0',
        'psutil==5.6.7',
        'PyYAML==5.2',
        'gitpython==3.1.1',
        'bcrypt==3.1.7',
        'speedtest-cli',
        'pexpect',
        'scapy',
        'lxml',
        'requests-cache',
        'peewee',
        'prettytable'
    ],
    # 命令行入口
    entry_points='''
        [console_scripts]
        m=src.ming:cli
    ''',
    author='ming',
    license='MIT',
    url='https://github.com/xujiuming/jiuming-tools',
    description='个人常用功能'
)
