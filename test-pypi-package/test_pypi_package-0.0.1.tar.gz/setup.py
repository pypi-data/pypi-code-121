from setuptools import setup, find_packages

VERSION = '0.0.1'
DESCRIPTION = 'Testing PyPI package'
LONG_DESCRIPTION = 'Setting up for practising and testing PyPi Packages'

# Setting up
setup(
    name="test_pypi_package",
    version=VERSION,
    author="Kishore Sampath",
    author_email="<skishore2602.dev@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=[],
    keywords=['python', 'testing', 'pypi'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
