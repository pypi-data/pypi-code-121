import setuptools


with open("README.md", "r") as fh:
    long_des = fh.read()

setuptools.setup(
    name='iyake_cn',
    version='0.5.5',
    author='Seon',
    packages=['iyake_cn'],
    author_email="781091978@qq.com",
    description="get key words from chinese content",
    long_description=long_des,
    long_description_content_type="text/markdown",
    url = 'https://blog.csdn.net/zohan134'
)
