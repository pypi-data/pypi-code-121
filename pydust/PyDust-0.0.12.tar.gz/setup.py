'''
setup.py - a setup script
Copyright (C) 2022 Tetsumune KISO
Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at
    http://www.apache.org/licenses/LICENSE-2.0
Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
Authors:
    Zsolt Horvath <zsolte@gmail.com>
'''

import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="PyDust",
    version="0.0.12",
    description="PyDust",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/MondoAurora/pydust/dust",
    author="Zsolt Horvath",
    author_email="zsolte@gmail.com",
    license="Apache License 2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    packages=["dust","dust.persist"],
    include_package_data=True,
    install_requires=["pytz", "python-dateutil", "pyyaml", "jinja2", "requests", "mysql-connector-python"]
)