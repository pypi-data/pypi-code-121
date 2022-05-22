import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="videoembed",
    version="1.0.0",
    author="Philipp Hewera",
    author_email="github.hewera@mailbox.org",
    description="Create embed codes from video URLs.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/phewera/videoembed",
    project_urls={
        "Bug Tracker": "https://github.com/phewera/videoembed/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "videoembed"},
    packages=setuptools.find_packages(where="videoembed"),
    python_requires=">=3.8",
    install_requires=[
        "requests",
    ],
)
