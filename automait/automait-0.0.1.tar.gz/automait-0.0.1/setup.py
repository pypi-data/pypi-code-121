import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="automait",
    version="0.0.1",
    author="Lukas Leuschen",
    author_email="lukas.leuschen@automait.ai",
    description="automait package for interfacing our modeling services",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/automait_public/automait_client",
    project_urls={
        "Bug Tracker": "https://gitlab.com/automait_public/automait_client/-/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
)