
from setuptools import setup, find_packages
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

# Arguments marked as "Required" below must be included for upload to PyPI.
# Fields marked as "Optional" may be commented out.

setup(
    name="VorGemeinde",
    version="0.2.0",  # Required
    description="Vorarlberger Gemeinden",  # Optional
    author_email="michael.mayer@student.htldornbirn.at",
    classifiers=[  # Optional

        "Development Status :: 3 - Alpha",
        # Indicate who your project is intended for
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        # Pick your license as you wish
        "License :: OSI Approved :: MIT License",
        # Specify the Python versions you support here. In particular, ensure
        # that you indicate you support Python 3. These classifiers are *not*
        # checked by 'pip install'. See instead 'python_requires' below.
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    # This field adds keywords for your project which will appear on the
    # project page. What does your project relate to?
    #
    # Note that this is a list of additional keywords, separated
    # by commas, to be used to assist searching for the distribution in a
    # larger catalog.
    keywords="Vorarlberg, Gemeinde, development",  # Optional
    # When your source code is in a subdirectory under the project root, e.g.
    # `src/`, it is necessary to specify the `package_dir` argument.
    package_dir={"": "src"},  # Optional
    packages=find_packages(where="src"),  # Required
    python_requires=">=3.7, <4",
    install_requires=["setuptools"],  # Optional
    extras_require={  # Optional
        "dev": ["check-manifest"],
        "test": ["coverage"],
    },
    package_data={  # Optional
        "VorGemeinde": ["package_data.dat"],
    },
    data_files=[("my_data", ["data/data_file"])],  # Optional
    entry_points={  # Optional
        "console_scripts": [
            "VorGemeinde=VorGemeinde:main",
        ],
    },
)
