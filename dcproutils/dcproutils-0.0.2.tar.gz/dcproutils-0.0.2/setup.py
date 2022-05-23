from setuptools import setup, find_packages

VERSION = '0.0.2'
DESCRIPTION = 'DcPro utilities'

setup(
	name="dcproutils",
	version=VERSION,
	author="Camel Blue",
	author_email="",
	description=DESCRIPTION,
	packages=find_packages(),
	install_requires=["datetime", "json", "requests"],
)