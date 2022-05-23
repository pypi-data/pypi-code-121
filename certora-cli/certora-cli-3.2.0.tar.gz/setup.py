import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

NAME = "certora-cli"
VERSION = "3.2.0"
DEPS = [
    "tabulate", "requests", "pycryptodome", "tqdm", "click", "sly"
]

if __name__ == "__main__":
    setuptools.setup(
        name=NAME,
        version=VERSION,
        author="Certora",
        author_email="support@certora.com",
        description="Utilities for building smart contracts for verification using the Certora Prover, and for running the Certora Prover",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/Certora/CertoraCLI",
        packages=setuptools.find_packages(),
        include_package_data=True,
        install_requires=DEPS,
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
        ],
        entry_points={
            "console_scripts": [
                "certoraRun = certora_cli.certoraRun:entry_point"
            ]
        },
        python_requires='>=3.5',
    )
