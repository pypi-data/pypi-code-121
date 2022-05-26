import setuptools

with open("readme.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setuptools.setup(
    author="Richard Dally",
    name="pysteamupload",
    version="0.1.3",
    description="SteamCMD leveraged by CPython to upload binaries",
    url="https://github.com/RichardDally/PySteamUpload",
    license="GNU Lesser General Public License v3.0",
    install_requires=requirements,
    packages=["pysteamupload"],
    package_dir={"pysteamupload": "pysteamupload"},
    package_data={"pysteamupload": ["templates/*.txt"]},
    include_package_data=True,
    author_email="r.dally@proton.me",
    long_description=long_description,
    long_description_content_type="text/markdown",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
    project_urls={
        "Issues": "https://github.com/RichardDally/PySteamUpload/issues",
        "Source Code": "https://github.com/RichardDally/PySteamUpload",
        "Releases": "https://github.com/RichardDally/PySteamUpload/releases"
    },
    python_requires='>=3.8',
)
