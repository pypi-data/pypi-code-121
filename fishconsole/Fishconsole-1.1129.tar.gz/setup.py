from setuptools import setup, find_packages
from Fishconsole import fcv

filepath = 'README.md'

setup(
    name="Fishconsole",
    version=fcv.version(),
    author="Fish Console",
    author_email="2645602049@qq.com",
    description="小鱼整理的控制台输出辅助模块",

    # 项目主页
    url="https://space.bilibili.com/698117971?spm_id_from=333.1007.0.0",
    # 长描述
    long_description=open(filepath, encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),

    # 依赖包，没有将会自动下载
    install_requires=['requests>=2.0', 'lxml>=4.0', 'easygui>=0.98.2', 'matplotlib>=3.5.1'],
)
