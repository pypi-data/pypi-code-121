import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name = "materials_visualization",
    version = "0.1.3",
    author = "Kevin Whitham",
    author_email = "kevin.whitham@gmail.com",
    description = "Routines to visualize atomic models in jupyter",
    long_description = long_description,
    long_description_content_type = "text/markdown",
    url = "https://github.com/kevinwhitham/materials_visualization.git",
    install_requires=   ["perovskite_intercalation>=0.0.6",
                         "nglview>=2.7.7",
                         "ase>=3.21.1",
                         "ipywidgets>=7.5.1",
                         "numpy>=1.20.2",
                         "gpaw>=20.10.0"],
    classifiers = [
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
            "Operating System :: OS Independent",
    ],

    package_dir = {"": "src"},
    packages = setuptools.find_packages(where="src"),
    python_requires = ">=3",
)

