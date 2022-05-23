import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name="SensorsABTestingSDK",
    version="0.0.2",
    author="Jianzhong YUE",
    author_email="yuejianzhong@sensorsdata.cn",
    description="This is the official Python ABTesting SDK for Sensors Analytics.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/sensorsdata/abtesting-sdk-python",
    packages=setuptools.find_packages(),
)
