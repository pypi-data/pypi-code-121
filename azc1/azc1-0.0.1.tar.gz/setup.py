from setuptools import setup, find_packages

setup(
    name="azc1",
    version="0.0.1",
    author="a1",
    author_email="xxx@123.com",
    description="你好",

    # 项目主页
    url="", 

    # 你要安装的包，通过 setuptools.find_packages 找到当前目录下有哪些包
    packages=find_packages(),
    python_requires='>=3.6',
)