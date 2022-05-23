from setuptools import setup
from setuptools import find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="mh",
    Version="0.0.33",
    author="Mark Hallett",
    author_email="mh@markhallett.co.uk",
    description="A small example package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/markhallett/mh",
    project_urls={
        "Documentation": "https://markhallett.github.io/mh",
    },
    packages=find_packages('src'),
    #packages=[],
    py_modules=["mh"],
    package_dir={'':'src'},
    install_requires=[],
    extras_require={"dev":[
                            "pycrunch-trace==0.1.5",
                            "behave==1.2.6",
                           ],},
    scripts=['README.md',],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
         ],
)
