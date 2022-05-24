# coding: utf-8

"""

"""

# Third Party Libraries
from setuptools import find_packages, setup  # noqa: H301


# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = ["urllib3 >= 1.15", "six >= 1.10", "certifi", "python-dateutil", "sseclient"]

setup(
    name="aristaflowpy",
    version="1.12.0",
    description="AristaFlow BPM",
    author_email="info@aristaflow.com",
    url="https://github.com/aristaflow/aristaflowpy",
    keywords=["AristaFlow", "BPM", "Workflow", "REST"],
    install_requires=REQUIRES,
    packages=find_packages(),
    include_package_data=True,
    long_description="""\
        AristaFlow BPM Python integration
        """,
)
