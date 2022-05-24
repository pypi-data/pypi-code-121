from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="databeaver",
    version="0.0.33",
    author="David Orkin",
    author_email="david.orkin@fuzzybumblebee.org",
    description="Data Model Orchestration",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://opensource.fuzzybumblebee.org/databeaver/latest",
    project_urls={
        "Bug Tracker": "https://github.com/FBB-David/databeaver/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
        "Operating System :: POSIX :: Linux"
    ],
    package_data={'databeaver': ['data/configSample.*']},
    install_requires=['tomli'],
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    scripts=['src/databeaver/bin/beaver']
)



