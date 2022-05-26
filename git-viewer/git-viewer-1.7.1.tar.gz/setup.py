#!/usr/bin/env python3

import setuptools
import site
import os

site.ENABLE_USER_SITE = os.geteuid() != 0

setuptools.setup(package_data={"":["doc/*"]})
