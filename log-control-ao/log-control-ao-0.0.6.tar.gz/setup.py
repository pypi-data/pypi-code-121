from setuptools import setup, find_packages

setup(
    name="log-control-ao",
    version="0.0.6",
    author="wangziling100",
    author_email="wangziling100@163.com",
    description="Exposed interface tool for accessing log controller api",
    package_dir={"": "src"},
    packages=find_packages(where='src'),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
    ],
)