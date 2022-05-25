import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="hcscom",
    version="0.5.8",
    author="Patrick Menschel",
    author_email="menschel.p@posteo.de",
    description="An interface class to manson hcs lab power supplies",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/menschel/hcscom",
    packages=setuptools.find_packages(exclude=['tests', ]),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: POSIX :: Linux",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering",
        "Topic :: Software Development :: Embedded Systems",
        "Topic :: Utilities",
    ],
    python_requires='>=3.7',
    install_requires=["pyserial",
                      "psutil",
                      ],
    keywords='remote psu power-supply',

)
