from setuptools import setup

import compileall

from os import path
# 读取readme文件，这样可以直接显示在主页上
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

compileall.compile_dir("src")

setup(
    name='fieldsTurn',
    version='1.0',
    packages=['fieldsturn'],
    url='',
    license='MIT',
    author='sanwen zhu',
    author_email='652187661@qq.com',
    description='',
    keywords='',
    python_requires='>=3.8',
    long_description=long_description,
    long_description_content_type='text/markdown',
    install_requires=['pandas']
)
