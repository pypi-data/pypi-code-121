from setuptools import setup

with open("README.md", "r") as fh:
     long_description = fh.read()

setup(
    name="netx_fdl_compiler",
    version="0.1.3",
    author="Paul Fox",
    author_email="paul.fox@temposonics.com",
    description="Flash device label compiler for Hilscher netX90",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/pfox89/netx_fdl_compiler.git",
    packages=['netx_fdl_compiler'],
    install_requires = ['construct', 'pyyaml'],
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Operating System :: OS Independent",
        "Topic :: Software Development :: Embedded Systems",
        "License :: OSI Approved :: Apache Software License"
    ],
    package_data={
        "":["*.json"],
    },
    include_package_data=True,
    python_requires='>=3.7'
)