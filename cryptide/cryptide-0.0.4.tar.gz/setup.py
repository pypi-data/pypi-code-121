import setuptools
from cryptide import __version__, __author__

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cryptide",  # Replace with your own username
    version=__version__,
    author=__author__,
    author_email="ursial.alain@gmail.com",
    description="To help you for les brutes force ",
    long_description=long_description,
    long_description_content_type="text/markdown",
    #url="https://github.com/pypa/sampleproject",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=['Unidecode', 'py-enigma']
)
