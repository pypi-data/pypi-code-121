import os
import shutil

from setuptools import find_packages
from setuptools import setup

###############################################################################
# Define variables
#
# Modify these values to fork a new plugin
#

author = "Synerty"
author_email = "contact@synerty.com"
py_package_name = "peek_plugin_base"
pip_package_name = py_package_name.replace("_", "-")
package_version = "3.1.6"
description = "Peek Plugin Base."

download_url = "https://bitbucket.org/synerty/%s/get/%s.zip"
download_url %= pip_package_name, package_version
url = "https://bitbucket.org/synerty/%s" % pip_package_name

###############################################################################


egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile("MANIFEST"):
    os.remove("MANIFEST")

requirements = [
    # Database packages
    "SQLAlchemy < 1.4.0",  # Database abstraction layer
    "SQLAlchemy-Utils >= 0.32.9",
    "alembic >= 0.8.7",  # Database migration utility
    "GeoAlchemy2",  # Geospatial addons to SQLAlchemy
    # networking and async framework. Peek is based on Twisted.
    "Twisted[tls,conch]",
    # Celery packages
    "txcelery-py3 >= 1.6.3",
    # The package for RW support
    "json-cfg-rw",
    # Protocol and data packages
    "pytmpdir < 1.0",
    # A temporary directory, useful for extracting archives to
    "txhttputil >= 1.0.2, <= 1.0.5",  # Utility class for http requests
    "vortexpy >= 3.0.0",
    # Data serialisation and transport layer, observable based
    # SOAP interface packages
    "SOAPpy-py3 >= 0.52.26",  # See http://soappy.ooz.ie for tutorials
    "wstools-py3 >= 0.54.2",
    "txsuds-py3 >= 0.5.9",
    # RxPY by Microsoft. Used everywhere
    # TODO Upgrade to rx 3.x.x
    "rx < 3.0.0",
    # Improve datetime support
    "pytz",
    "tzlocal",
]

###############################################################################
# Define the dependencies

# Ensure the dependency is the same major number
# and no older then this version

# Not required for peek-plugin-base

###############################################################################
# Call the setuptools

setup(
    name=pip_package_name,
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
    install_requires=requirements,
    zip_safe=False,
    version=package_version,
    description=description,
    author=author,
    author_email=author_email,
    url=url,
    download_url=download_url,
    keywords=["Peek", "Python", "Platform", "synerty"],
    classifiers=[],
)
