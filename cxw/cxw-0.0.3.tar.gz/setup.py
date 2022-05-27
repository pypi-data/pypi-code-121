from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="cxw",
    version="0.0.3",
    author="xuanzhi33",
    author_email="xuanzhi33@qq.com",
    description="A small package to display error message in a fun way.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    license="GPL-3.0",
    packages=find_packages(),
    python_requires=">=3.6"
)
