# -*- coding: utf-8 -*-
from setuptools import find_namespace_packages
from setuptools import setup


setup(
    name="namespaceexample.native",
    version="1.0a1",
    description="An add-on for Plone",
    long_description="long_description",
    author="Maurits van Rees",
    author_email="m.van.rees@zestsoftware.nl",
    license="GPL version 2",
    packages=find_namespace_packages("src"),
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
    ],
    entry_points="""
    [z3c.autoinclude.plugin]
    target = plone
    """,
)
