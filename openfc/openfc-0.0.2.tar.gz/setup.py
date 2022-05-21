import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="openfc",
    version="0.0.2",
    author="Daniel Chen",
    author_email="danielcxh@icloud.com",
    description="An Open Financial Database",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://gitee.com/danielcxh/openfc",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "pandas==1.1.5", "requests==2.22.0", "xlrd>=1.2.0",
        "pyexcel-xls==0.7.0", "yapf==0.32.0", "beautifulsoup4==4.11.1",
        "mplfinance==0.12.8b9", "py-mini-racer == 0.6.0"
    ],
)
