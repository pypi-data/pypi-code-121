import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="wintertoo",
    version="0.2.1",
    author="Danielle Frostig, Viraj Karambelkar, Robert Stein",
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    url="https://github.com/winter-telescope/wintertoo",
    keywords="astronomy image WINTER",
    packages=setuptools.find_packages(),
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires='>=3.7',
    install_requires=[
        "astropy",
        "astroquery",
        "coveralls",
        "docker",
        "pandas",
        "psycopg[binary]",
        "jupyter",
        "matplotlib",
        "numpy",
        "pandas",
        "wtforms",
        "sqlalchemy",
        "astroplan",
        "email_validator",
        "pytz",
    ],
    package_data={
        'wintertoo': [
            'data/*.json',
            "data/summer_fields.txt"
        ],
        "tests": [
            "testdata/*.json"
        ]
    }
)
