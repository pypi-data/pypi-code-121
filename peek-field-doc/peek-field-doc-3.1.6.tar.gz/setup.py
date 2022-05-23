import os
import shutil
import subprocess
from subprocess import CalledProcessError

from setuptools import setup, find_packages

###############################################################################
# Define variables
#
# Modify these values to fork a new plugin
#

author = "Synerty"
author_email = "contact@synerty.com"
py_package_name = "peek_field_doc"
pip_package_name = py_package_name.replace("_", "-")
package_version = "3.1.6"
description = "Peek Developer Documentation."

download_url = "https://bitbucket.org/synerty/%s/get/%s.zip"
download_url %= pip_package_name, package_version
url = "https://bitbucket.org/synerty/%s" % pip_package_name

###############################################################################
# Customise the package file finder code

egg_info = "%s.egg-info" % pip_package_name
if os.path.isdir(egg_info):
    shutil.rmtree(egg_info)

if os.path.isfile("MANIFEST"):
    os.remove("MANIFEST")

excludePathContains = (
    "__pycache__",
    "node_modules",
    "platforms",
    "dist",
    "doc_link",
    "doc_dist",
    "doc_dist_latex",
)
excludeFilesEndWith = (".pyc", ".js", ".js.map", ".lastHash")
excludeFilesStartWith = ("peek_plugin",)


def find_package_files():
    paths = []
    for (path, directories, filenames) in os.walk(py_package_name):
        if [e for e in excludePathContains if e in path]:
            continue

        for filename in filenames:
            if [e for e in excludeFilesEndWith if filename.endswith(e)]:
                continue

            if [e for e in excludeFilesStartWith if filename.startswith(e)]:
                continue

            relPath = os.path.join(path, filename)
            try:
                subprocess.check_call(["git", "check-ignore", "-q", relPath])

            except CalledProcessError:
                paths.append(relPath[len(py_package_name) + 1 :])

    return paths


package_files = find_package_files()

###############################################################################
# Define the dependencies

# Ensure the dependency is the same major number
# and no older then this version

requirements = [
    "peek_plugin_base",
    "sphinx<4",
    "sphinx-autobuild",
    "sphinx-rtd-theme",
]

# Force the dependencies to be the same branch
reqVer = ".".join(package_version.split(".")[0:2]) + ".*"

# >=2.0.*,>=2.0.6
requirements = [
    "%s==%s,>=%s" % (pkg, reqVer, package_version.split("+")[0])
    if pkg.startswith("peek")
    else pkg
    for pkg in requirements
]

###############################################################################
# Call the setuptools

setup(
    name=pip_package_name,
    packages=find_packages(
        exclude=["*.tests", "*.tests.*", "tests.*", "tests"]
    ),
    package_data={"": package_files},
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
