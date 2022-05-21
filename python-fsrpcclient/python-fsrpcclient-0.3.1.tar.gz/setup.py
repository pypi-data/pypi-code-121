#!/usr/bin/env python3
import os
try:
	from setuptools import setup # type: ignore
except ImportError:
	from distutils.core import setup

pwd = os.path.abspath(os.path.dirname(__file__))

setup(
	name                          = "python-fsrpcclient",
	version                       = "0.3.1",
	description                   = "Fusion Solutions RPC client",
	keywords                      = "json rpc client fusion solutions fusionsolutions",
	author                        = "Andor `iFA` Rajci - FUSION SOLUTIONS KFT",
	author_email                  = "ifa@fusionsolutions.io",
	url                           = "https://github.com/FusionSolutions/python-fsrpcclient",
	license                       = "GPL-3",
	packages                      = ["fsRPCClient"],
	long_description              = open(os.path.join(pwd, "README.md")).read(),
	long_description_content_type = "text/markdown",
	zip_safe                      = False,
	python_requires               = ">=3.8.0",
	install_requires              = ["python-fslogger~=0.2.0", "python-fssignal~=0.1.0", "python-fspacker~=0.2.0", "lz4"],
	test_suite                    = "fsRPCClient.test",
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
