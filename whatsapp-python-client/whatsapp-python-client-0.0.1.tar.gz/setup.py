from os import path
from setuptools import setup

# read the contents of your description file

this_directory = path.abspath(path.dirname(__file__))
requirementPath = this_directory + '/requirements.txt'
install_requires = []
if path.isfile(requirementPath):
    with open(requirementPath) as f:
        install_requires = f.read().splitlines()
setup(
    name="whatsapp-python-client",
    version="0.0.1",
    description="Opensource python wrapper to WhatsApp Cloud API",
    url="https://github.com/open-code-ocean/whatsapp-python-client.git",
    author="Sagar Gajare",
    author_email="sggajare360@gmail.com",
    license="MIT",
    packages=["whatsbot"],
    keywords=[
        "PyWhatsApp",
        "WhatsApp API in Python Cilent",
        "whatsbot",
        "whatsbot-libary",
        "WhatsApp Cloud API Wrapper",
        "WhatsApp API in Python",
        "WhatsApp API in Python Wrapper",
    ],
    python_requires=">=3.6",
    install_requires=install_requires,
)