from setuptools import setup, find_packages

setup(
    name="k3s-control-ao",
    version="0.0.25",
    author="wangziling100",
    author_email="wangziling100@163.com",
    description="Exposed interface for accessing k3s controller",
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)