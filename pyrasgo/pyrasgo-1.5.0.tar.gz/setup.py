from pathlib import Path
import re
from setuptools import setup


here = Path(__file__).absolute().parent

version_content = Path(here, "pyrasgo", "version.py").read_text(encoding="utf-8")
version_attrs = dict(re.findall(r"__([a-z]+)__ *= *['\"](.+)['\"]", version_content))
long_description = Path(here / "DESCRIPTION.md").read_text(encoding="utf-8")
requirements = Path(here / "requirements.txt").read_text(encoding="utf-8").splitlines()
sf_requirements = Path(here / "requirements-snowflake.txt").read_text(encoding="utf-8").splitlines()
bq_requirements = Path(here / "requirements-bigquery.txt").read_text(encoding="utf-8").splitlines()
setup(
    name="pyrasgo",
    version=version_attrs["version"],
    description="Python interface to the Rasgo API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Patrick Dougherty",
    author_email="patrick@rasgoml.com",
    url="https://www.rasgoml.com/",
    license="GNU Affero General Public License v3 or later (AGPLv3+)",
    project_urls={
        "Documentation": "https://docs.rasgoml.com",
        "Source": "https://github.com/rasgointelligence/RasgoSDKPython",
        "Rasgo": "https://www.rasgoml.com/",
        "Changelog": "https://github.com/rasgointelligence/RasgoSDKPython/blob/master/pyrasgo/CHANGELOG.md",
    },
    packages=[
        "pyrasgo",
        "pyrasgo.api",
        "pyrasgo.primitives",
        "pyrasgo.schemas",
        "pyrasgo.storage",
        "pyrasgo.storage.dataframe",
        "pyrasgo.storage.datawarehouse",
        "pyrasgo.utils",
    ],
    install_requires=requirements,
    extras_require={
        "snowflake": sf_requirements,
        "bigquery": bq_requirements,
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Scientific/Engineering :: Information Analysis",
    ],
)
