from setuptools import setup, find_packages

VERSION = '0.0.0'
DESCRIPTION = 'A SchoolWare Wrapper writen in Python'
LONG_DESCRIPTION = open("README.md").read()

# Setting up
setup(
    name="schoolware",
    version=VERSION,
    author="Bjarne Verschorre",
    author_email="bjarne.verschorre@protonmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'schoolware', 'school', 'wrapper'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
