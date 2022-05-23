import os
import shutil

from setuptools import find_packages
from setuptools import setup

from peek_platform.WindowsPatch import isWindows

###############################################################################
# Define variables
#
# Modify these values to fork a new plugin
#

author = "Synerty"
author_email = "contact@synerty.com"
py_package_name = "peek_platform"
pip_package_name = py_package_name.replace("_", "-")
package_version = "3.1.6"
description = "Peek Platform."

download_url = "https://bitbucket.org/synerty/%s/get/%s.zip"
download_url %= pip_package_name, package_version
url = "https://bitbucket.org/synerty/%s" % pip_package_name

###############################################################################

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile("MANIFEST"):
    os.remove("MANIFEST")

# pip install flower==0.7.3 tornado==3.2.2


requirements = [
    # packages used for the platform to test and upgrade it's self
    "pip >= 21.0",
    "virtualenv >= 15.1.0",
    "twine",
    # networking and async framework. Peek is based on Twisted.
    "Cython >= 0.21.1",
    "Twisted[tls,conch]",
    "pyOpenSSL <= 19.1.0", # PEEK-1136
    "pyasn1 >= 0.1.9",
    "pyasn1-modules >= 0.0.8",
    # Database
    "psycopg2-binary >= 2.7.6",  # PostGreSQL for Linux
    "SQLAlchemy < 1.4.0",  # Database abstraction layer
    "SQLAlchemy-Utils >= 0.32.9",
    "alembic >= 0.8.7",  # Database migration utility
    # installed and configured first
    # Utilities
    "python-dateutil >= 2.6.0",
    "Pygments >= 2.0.1",  # Generate HTML for code that is syntax styled
    "watchdog >= 0.8.3",
    # Used to detect file changes and re-copy them for frontend builds
    # Licensing
    "pycryptodome",
    # Celery packages
    "flower",
    # "amqp >= 1.4.9",  # DEPENDENCY LINK BELOW
    # Potentially useful packages
    # "GitPython >= 2.0.8",
    # "jira",
    # "dxfgrabber >= 0.7.4",
    # Peek platform dependencies, all must match
    "peek-plugin-base",  ##==%s" % py_package_name,
    "peek-core-device",  ##==%s" % py_package_name,
    "peek-core-email",  ##==%s" % py_package_name,
    # Memory logging
    "psutil",
]

lin_dependencies = [
    # We still require shapely on windows, but we need to manually download the win wheel
    "Shapely >= 1.5.16",  # Geospatial shape manipulation
    # We still require pymssql on windows, but we need to manually download the win wheel
    "pymssql",
    # Celery 4 is not supported on windows
    "future",  # This is required by celery
    "celery[redis,auth]<5.0.0",
]

win_dependencies = [
    # "pymssql >= 2.1.3",  # DB-API interface to Microsoft SQL Server, requires FreeTDS
    "pycparser >= 2.17",
    "cffi >= 1.9.1",
    "cryptography <= 3.1.1",  # PEEK-1136
    "pytest >= 3.0.5",
    "wheel >= 0.33.1.6",
    "virtualenv >= 15.1.0",
    # Celery 4 is not supported on windows
    "celery[redis,auth]<4.0.0",
    # Service support for windows
    "pypiwin32",
]

if isWindows:
    requirements.extend(win_dependencies)

else:
    requirements.extend(lin_dependencies)

# Packages that are presently installed from a git repo
# See http://stackoverflow.com/questions/17366784/setuptools-unable-to-use-link-from-dependency-links/17442663#17442663
dependency_links = [
    # Celery packages
    # "git+https://github.com/celery/py-amqp#egg=amqp",
]

dev_requirements = [
    "coverage >= 4.2",
    "mock >= 2.0.0",
    "selenium >= 2.53.6",
]

requirements.extend(dev_requirements)

###############################################################################
# Define the dependencies

# Ensure the dependency is the same major number
# and no older then this version

# Force the dependencies to be the same branch
reqVer = ".".join(package_version.split(".")[0:2]) + ".*"

# >=2.0.*,>=2.0.6
requirements = [
    "%s==%s,>=%s" % (pkg, reqVer, package_version.split("+")[0]) if pkg.startswith(
        "peek") else pkg
    for pkg in requirements
]

###############################################################################
# Call the setuptools

setup(
    entry_points={
        "console_scripts": [
            "winsvc_peek_restarter = peek_platform.winsvc_peek_restarter:main",
        ],
    },
    name=pip_package_name,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]),
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
