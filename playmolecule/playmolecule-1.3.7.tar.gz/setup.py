import setuptools
import subprocess

try:
    version = (
        subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
        .strip()
        .decode("utf-8")
    )
except Exception as e:
    print(f"Could not get version tag with error {e}. Defaulting to version 0")
    version = "0"

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

if __name__ == "__main__":
    with open("README.md", "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="playmolecule",
        version=version,
        author="Acellera",
        author_email="info@acellera.com",
        description="The playmolecule python code.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/acellera/playmolecule-python-api/",
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: POSIX :: Linux",
        ],
        packages=setuptools.find_packages(include=["playmolecule*"], exclude=[]),
        package_data={
            "playmolecule": ["config.ini", "logging.ini"],
        },
        install_requires=requirements,
    )
