import setuptools

with open("README.rst", "r") as fh:
    long_description = fh.read()

with open('requirements.txt', 'r') as fh:
    requirements = fh.read().splitlines()


setuptools.setup(
    name="endi_split_pdf",
    version="1.0.9",
    author="Arezki Feth",
    author_email="tech@majerti.fr",
    description="Splits specific PDF files and stores the result in a custom directory layout",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU General Public License (GPL)",
        "Operating System :: OS Independent",
    ],
    scripts=[
        'scripts/endi-split-pdf-run',
        'scripts/endi-split-pdf-page2text',
        'change_code_analytique',
    ],
    zip_safe=False,
    python_requires='>=3.6',
    install_requires=requirements,
    extras_require={
        'dev': ['pytest'],
    },
)
