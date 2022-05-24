# -*- coding: utf-8 -*-
from setuptools import find_packages
from setuptools import setup


setup(
    name="example.addon",
    version="1.0a1",
    description="An add-on for Plone",
    long_description="long_description",
    author="Maurits van Rees",
    author_email="m.van.rees@zestsoftware.nl",
    license="GPL version 2",
    packages=find_packages("src", exclude=["ez_setup"]),
    namespace_packages=["example"],
    package_dir={"": "src"},
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "setuptools",
    ],
    # I want to try without setting a target in the entry point.
    # We could choose to say that when loading all zcml for a specific target,
    # we also load all zcml without a target.
    # Such a package basically says: load my zcml always.
    # zc3.autoinclude ignores the target option (and all options) anyway, it seems.
    #
    # Problems:
    # 1. Without setting any options, the entry point is not available.
    # 2. With an empty target, installing the package utterly fails.
    # For now, add a dummy option, so we can check this scenario.
    entry_points="""
    [z3c.autoinclude.plugin]
    dummy = dummy
    """,
)
