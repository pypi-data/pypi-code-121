import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="PyCRX",
    version="0.0.420",
    author="Cr1tical",
    author_email="critical@criticalfn.ml",
    description="Used for functions in PyCRX OS",
    long_description=long_description, # don't touch this, this is your README.md
    long_description_content_type="text/markdown",
    url="https://replit.com/@cr1tical/PyCRXpkg?monaco=1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)