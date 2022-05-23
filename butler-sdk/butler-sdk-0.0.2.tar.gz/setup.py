"""
    Butler Python SDK

    Provides functions to use Butler REST API easily.

    Details on the API can be found here: https://docs.butlerlabs.ai/reference/welcome
"""


from setuptools import setup, find_packages  # noqa: H301

NAME = "butler-sdk"
VERSION = "0.0.2"
# To install the library, run the following
#
# python setup.py install
#
# prerequisite: setuptools
# http://pypi.python.org/pypi/setuptools

REQUIRES = [
  "urllib3 >= 1.25.3",
  "python-dateutil",
]

setup(
    name=NAME,
    version=VERSION,
    description="Butler Python SDK",
    author="Butler Labs",
    author_email="support@butlerlabs.ai",
    url="https://butlerlabs.ai",
    project_urls={
      "Documentation": "https://docs.butlerlabs.ai/reference/welcome"
    },
    keywords=["Butler", "AutoML", "OCR"],
    python_requires=">=3.6",
    install_requires=REQUIRES,
    packages=find_packages(exclude=["test", "tests"]),
    include_package_data=True,
    long_description="""\
           Welcome to Butler Python SDK # noqa: E501
    """
)
