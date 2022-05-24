# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name="example.multipleeps",
    version="1.0a1",
    description="An add-on for Plone",
    long_description="long_description",
    author="Thomas Schorr",
    author_email="t_schorr@gmx.de",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["example"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
    ],
    entry_points={
        "z3c.autoinclude.plugin": [
            "dummy = dummy",
        ],
        "plone.autoinclude.plugin": [
            "target = plone",
            "module = example.multipleeps",
        ],
    },
)
