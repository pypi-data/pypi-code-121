from setuptools import setup, find_packages

setup(
    name = "trigo",
    version = "0.3",
    description = "Package to calculate trigonometric ratios",
    author = "Sahil Rajwar",
    author_email = "justsahilrajwar2004@gmail.com",
    packages = ["trigo"],
    license = "MIT",
    install_requires = ["numpy"],
    url = "",
    long_description = open("README.txt").read() + "\n\n" + open("CHANGELOG.txt").read(),
    keywords = ["trigonometry","trigo","calculator"],
    classifiers = [
    "Programming Language :: Python :: 3",
    "Intended Audience :: Education",
    "Operating System :: Microsoft :: Windows",
    "License :: OSI Approved :: MIT License"
    ]
)
