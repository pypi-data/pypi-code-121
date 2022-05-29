from setuptools import setup, find_packages
import codecs
import os

here = os.path.abspath(os.path.dirname(__file__))

with codecs.open(os.path.join(here, "README.md"), encoding="utf-8") as fh:
    long_description = "\n" + fh.read()

VERSION = "0.0.5"
DESCRIPTION = "Field Emission Data Postprocessing and Data Provider"
LONG_DESCRIPTION = "This packages provides a bunch of classes and methods to handle field emission data (based on files of Field Emission Data AQuisition (FEMDAQ written in C#) measurement tool of the OTH-Regensburg. (GIT-link for the measurement tool may be released in future.)"

# Setting up
setup(
    name="FieldEmission",
    version=VERSION,
    author="haum@oth",
    author_email="<matthias.hausladen@oth-regensburg.de>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=["numpy", "re", "enum", "math", "scipy"],
    keywords=["python", "Cold Field Emission", "Fowler Nordheim"],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft :: Windows",
    ],
)
