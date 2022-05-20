"""
Setup the package.
"""

from setuptools import setup, find_packages

with open("README.md", mode='r', encoding="utf-8") as readme:

    project_description = readme.read()

setup(

    name="star-slayer",

    packages=find_packages(),

    package_data={

        "starslayer" : ["json/keys/*.json",
                        "json/profiles/*.json",
                        "textures/icon/*.gif",
                        "textures/player/star_slayer/*.customppm",
                        "textures/player/bilby_tanka/*.customppm",
                        "textures/player/viper_dodger/*.customppm"]
    },

    version="0.1.0-alpha",

    url="https://github.com/NLGS2907/star-slayer",

    author="NLGS",

    author_email="flighterman@fi.uba.ar",

    license="MIT",

    description="Little game made with Gamelib",

    long_description=project_description,

    long_description_content_type="text/markdown",

    classifiers=[

        "Development Status :: 3 - Alpha",

        "License :: OSI Approved :: MIT License",

        "Programming Language :: Python :: 3.10"
    ]
)
