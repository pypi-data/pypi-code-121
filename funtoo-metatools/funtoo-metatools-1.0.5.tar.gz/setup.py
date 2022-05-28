import setuptools
from subpop.pkg import Packager, SubPopSetupInstall

pkgr = Packager()

with open("README.rst", "r") as fh:
	long_description = fh.read()

setuptools.setup(
	name="funtoo-metatools",
	version="1.0.5",
	author="Daniel Robbins",
	author_email="drobbins@funtoo.org",
	description="Funtoo framework for auto-creation of ebuilds.",
	long_description=long_description,
	long_description_content_type="text/x-rst",
	url="https://code.funtoo.org/bitbucket/users/drobbins/repos/funtoo-metatools/browse",
	scripts=["bin/doit"],
	classifiers=[
		"Programming Language :: Python :: 3",
		"License :: OSI Approved :: Apache Software License",
		"Operating System :: POSIX :: Linux",
	],
	python_requires=">=3.7",
	install_requires=[
		"subpop >= 2.0.0",
		"beautifulsoup4",
		"dict_toolbox",
		"httpx < 0.23.0",
		"Jinja2 >= 3",
		"packaging",
		"psutil",
		"pymongo",
		"PyYAML",
		"toml",
		"xmltodict",
		"colorama",
	],
	packages=setuptools.find_packages(),
	data_files=pkgr.generate_data_files(),
	cmdclass={"install": SubPopSetupInstall},
)

# vim: ts=4 sw=4 noet
