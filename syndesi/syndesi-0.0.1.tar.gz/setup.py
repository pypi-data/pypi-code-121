from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Syndesi test platform'

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Setting up
setup(
    name="syndesi",
    version=VERSION,
    author="Sebastien Deriaz",
    author_email="sebastien.deriaz1@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['numpy'],
    keywords=['python', 'syndesi', 'test', 'platform', 'measurment', 'testbench'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Education",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows"
    ]
)