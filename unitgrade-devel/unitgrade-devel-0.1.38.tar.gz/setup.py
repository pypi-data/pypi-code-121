# Use this guide:
# https://packaging.python.org/tutorials/packaging-projects/
# py -m build && twine upload dist/*
import setuptools
with open("src/unitgrade_private/version.py", "r", encoding="utf-8") as fh:
    __version__ = fh.read().strip().split(" = ")[1].strip()[1:-1]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="unitgrade-devel",
    version=__version__,
    author="Tue Herlau",
    author_email="tuhe@dtu.dk",
    description="A set of tools to develop unitgrade tests and reports and later evaluate them",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url='https://lab.compute.dtu.dk/tuhe/unitgrade_private',
    project_urls={
        "Bug Tracker": "https://lab.compute.dtu.dk/tuhe/unitgrade_private/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=['numpy', "unitgrade", "codesnipper", 'tabulate', 'tqdm', "pyfiglet",
                      "colorama", "coverage", 'mosspy', 'pyminifier', 'mosspy'],
)
