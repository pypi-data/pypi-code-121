import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geneburden",
    version="0.0.1",
    author="Zach Weber",
    author_email="zach.weber.813@gmail.com",
    description="Tools for testing variant burden in genomic features",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/zwebbs/geneburden",
    project_urls={
        "Bug Tracker": "https://github.com/zwebbs/geneburden/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.7",
    install_requires=[],
    entry_points={'console_scripts': {
        'geneburden=scripts.main:main'
        }
    }
)
