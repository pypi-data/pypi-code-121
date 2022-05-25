#!/usr/bin/env python
from setuptools import find_packages, setup


project = "witcher"
version = "0.0.31"
#scripts=["witcher.py","Recommender_system.py"]

setup(
    name=project,
    py_modules=[project],
    package_dir={"./":"src"},
    version=version,
    description="Automated AI tool including: recommender system, deep Learnings ...",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="Babak EA, Founder and CEO: AI Forest Inc ",
    author_email="emami.babak@gmail.com",
    url="https://github.com/BabakEA/witcher",
    packages=find_packages(exclude=["*.tests", "*.tests.*", "tests.*", "tests",]),
    

    include_package_data=True,
    zip_safe=False,
    install_requires=[
	"stdlib_list>=0.6.0",
	"ipywidgets==7.5.1",
        "pandas",
        "sklearn",
        "traitlets",
        "IPython",
        "statsmodels",
        "seaborn",
        "matplotlib",
        "yfinance",
        "pmdarima",
        "opencv-python"

    ],
    setup_requires=[
        "nose>=1.3.7",
    ],
    extras_require={
        "test": [
            "IPython >= 7.12.0",
            "notebook >=6.0.1",
        ],
    },
)
