from setuptools import setup, find_packages

VERSION = '2.0.3'
DESCRIPTION = 'Making connection between bython and Node-RED'
LONG_DESCRIPTION = 'This package send and recieve data with Node-RED'

# Setting up
setup(
    name="am_red_channel",
    version=VERSION,
    author="Amr Mostafa (Amr_MAM)",
    author_email="<amr.mostafa.abbas@gmail.com>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    install_requires=['requests'],
    keywords=['python', 'video', 'stream', 'video stream', 'camera stream', 'sockets', 'Node-RED'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)