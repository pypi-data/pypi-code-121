import setuptools
import subprocess


try:
    version = (
        subprocess.check_output(["git", "describe", "--abbrev=0", "--tags"])
        .strip()
        .decode("utf-8")
    )
except Exception:
    print("Could not get version tag. Defaulting to version 0")
    version = "0"

if __name__ == "__main__":
    with open("README.md", "r") as fh:
        long_description = fh.read()

    setuptools.setup(
        name="protocolinterface",
        version=version,
        author="Acellera",
        author_email="info@acellera.com",
        description="ProtocolInterface: A class to make python classes validate arguments.",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/acellera/protocolinterface/",
        classifiers=[
            "Programming Language :: Python :: 3.6",
            "Operating System :: POSIX :: Linux",
        ],
        packages=setuptools.find_packages(include=["protocolinterface*"], exclude=[]),
        install_requires=[],
    )
