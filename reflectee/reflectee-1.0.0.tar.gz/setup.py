import os
import re

from setuptools import setup

VERSION = os.environ.get("VERSION", "1.0.0.dev0")
VERSION = re.sub("-develop\.(\d+)", "-dev\\1", VERSION)
VERSION = re.sub("-alpha\.(\d+)", "-pos\\1", VERSION)

setup(
    version=VERSION,
)
