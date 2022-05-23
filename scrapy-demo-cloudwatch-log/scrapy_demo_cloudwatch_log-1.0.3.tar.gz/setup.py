from setuptools import setup, find_packages
from pathlib import Path

long_description = (Path(__file__).parent / "README.md").read_text()

setup(
    name="scrapy_demo_cloudwatch_log",
    long_description=long_description,
    long_description_content_type="text/markdown",
    version="1.0.3",
    license="MIT",
    author="Dimitrios Kouzis-Loukas",
    author_email="lookfwd@gmail.com",
    py_modules=["scrapy_demo_cloudwatch_log"],
    url="https://github.com/scalingexcellence/scrapy-demo-cloudwatch-log",
    keywords="scrapy cloudwatch aws json",
    install_requires=[
        "scrapy",
    ],
)
