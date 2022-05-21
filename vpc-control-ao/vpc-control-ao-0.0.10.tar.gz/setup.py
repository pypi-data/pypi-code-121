from setuptools import setup, find_packages

setup(
    name="vpc-control-ao",
    version="0.0.10",
    author="wangziling100",
    author_email="wangziling100@163.com",
    description="Exposed interface tool for accessing vpc controller api",
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)