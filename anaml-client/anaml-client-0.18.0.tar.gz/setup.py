#
# Copyright 2020 Simple Machines Pty Ltd - All Rights Reserved.
#
# This file is part of Anaml.
#
# Unauthorized copying and/or distribution of this file, via any medium
# is strictly prohibited.
#

import os
import re
import subprocess

from pkg_resources import packaging
from setuptools import setup, find_namespace_packages


# Allow the CI process to compute the version for us.
if "anaml_version" in os.environ:
    version = os.environ['anaml_version']
    # Check that version is a valid version string.
    _parsed_version = packaging.version.parse(version)
else:
    # Get version number from git tags
    rev_parse = subprocess.run(
        ['git', 'describe'], check=True, stdout=subprocess.PIPE, universal_newlines=True
    )
    status = subprocess.run(
        ['git', 'status', '--porcelain'], check=True, stdout=subprocess.PIPE, universal_newlines=True
    )
    if rev_parse.returncode == 0 and rev_parse.returncode == 0:
        modified = len(status.stdout) > 0
        if modified:
            flag = ".m"
        else:
            flag = ""
        version = rev_parse.stdout.strip().replace("release-v", "") + flag
        # Change git describe output to be valid for Python (PEP 400)
        version = re.sub(pattern="-([0-9]+)-([a-z0-9]+)", repl="+\\1.\\2", string=version)
    else:
        print("Unable to determine version number from git tags")
        exit(1)

# As far as I can tell, there's no other way to access this from within the module other than
# by munging the source code at install time.
with open("src/anaml_client/version.py", "w") as f:
    f.write(f"""#
#  Copyright 2021 Simple Machines Pty Ltd - All Rights Reserved.
#
#  This file is part of Anaml.
#
#  Unauthorized copying and/or distribution of this file, via any medium
#  is strictly prohibited.
#
\"\"\"Version metadata for the package.\"\"\"

__version__ = "{version}"
""")

long_description = """
The Anaml Python SDK makes it easy to interact with the [Anaml][1] feature
engineering platform from Python. The SDK provides datatypes and methods to
interact with the Anaml REST API and to load Anaml feature data into Pandas
and/or Spark data frames.

[1]: https://www.anaml.com/
"""

setup(
    name="anaml-client",
    version=version,
    author="Simple Machines",
    author_email="hello@simplemachines.com.au",
    description="Python SDK for Anaml",
    long_description=long_description,
    long_description_content_type='text/markdown',
    url="https://anaml.com",
    license="Copyright 2020 Simple Machines Pty Ltd. All Rights Reserved",
    classifiers=[
        'Programming Language :: Python :: 3',
        'Operating System :: OS Independent',
        'License :: Other/Proprietary License'
    ],
    # Package contents.
    packages=find_namespace_packages('src'),
    package_dir={'': 'src'},
    include_package_data=True,
    test_suite="tests",
    # Requirements and dependencies
    python_requires='>=3.7.10',
    install_requires=[
        "isodate",
        "jsonschema",
        "requests",
    ],
    extras_require={
        "testing": [
            "flake8",
            "flake8-copyright",
            "flake8-docstrings",
            "hypothesis[zoneinfo]",
            "parameterized",
            "pyarrow",
            "pytest",
            "pyspark",
            "pandas>=0.24"
        ],
        # Libraries
        "plotting": [
            "matplotlib",
            "pandas>=0.24"
            "seaborn",
        ],
        "pandas": [
            "numpy",
            "pandas>=0.24"
            "scipy",
        ],
        "spark": [
            "pyspark",
        ],
        # Cloud providers
        "aws": [
            "s3fs",
        ],
        "google": [
            "gcsfs",
            "google-cloud-bigquery[bqstorage,pandas]",
        ],
    },
)
