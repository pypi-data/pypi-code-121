from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1.8.9.4'
DESCRIPTION = 'An echo state network implementation.'
LONG_DESCRIPTION = 'An echo state network implementation, used in my PhD research as part of the DeepTurb project of the Carl-Zeiss Stiftung.'

# Setting up
setup(
    name="turbESN",
    version=VERSION,
    author="flohey (Florian Heyder)",
    author_email="<florian.heyder@tu-ilmenau.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['numpy', 'multiprocess', 'h5py', 'scipy'],
    python_requires=">=3.6.0",
    keywords=['python', 'ESN', 'reservoir computing', 'echo state network', 'recurrent neural network'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
