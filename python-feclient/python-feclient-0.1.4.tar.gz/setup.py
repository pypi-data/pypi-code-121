#!/usr/bin/env python3
import os
try:
	from setuptools import setup # type: ignore
except ImportError:
	from distutils.core import setup

pwd = os.path.abspath(os.path.dirname(__file__))

setup(
	name                          = "python-feclient",
	version                       = "0.1.4",
	description                   = "Client for Fusion Explorer",
	keywords                      = "explorer client fusion solutions fusionsolutions fusionexplorer",
	author                        = "Andor `iFA` Rajci - Fusions Solutions KFT",
	author_email                  = "ifa@fusionsolutions.io",
	url                           = "https://github.com/FusionSolutions/python-feclient",
	license                       = "GPL-3",
	packages                      = ["feClient"],
	long_description              = open(os.path.join(pwd, "README.md")).read(),
	long_description_content_type = "text/markdown",
	zip_safe                      = False,
	scripts                       = ["feClient/fexplorer-cli"],
	python_requires               = ">=3.8.0",
	install_requires              = ["python-fsrpcclient~=0.3.0"],
	test_suite                    = "feClient.test",
	package_data                  = { "":["py.typed"] },
	classifiers                   = [ # https://pypi.org/pypi?%3Aaction=list_classifiers
		"Development Status :: 4 - Beta",
		"Topic :: Utilities",
		"Programming Language :: Python :: 3 :: Only",
		"Programming Language :: Python :: 3.8",
		"Programming Language :: Python :: 3.9",
		"License :: OSI Approved :: GNU Lesser General Public License v3 or later (LGPLv3+)",
	],
)