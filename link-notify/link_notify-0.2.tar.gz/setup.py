from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = '0.2'
DESCRIPTION = 'Creates notification with button'
LONG_DESCRIPTION = 'Easily create notification with buttons that can open links'

# Setting up
setup(
    name="link_notify",
    version=VERSION,
    author="Prog Bits",
    author_email="progbitsprojects@gmail.com",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    install_requires=['ctypes', 'webbrowser'],
    keywords=['python', 'notification', 'notification with buttons', 'create notifications', 'notification with links'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)