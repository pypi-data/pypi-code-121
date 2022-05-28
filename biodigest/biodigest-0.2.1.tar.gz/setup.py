import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="biodigest",
    version="0.2.1",
    author="Klaudia Adamowicz",
    author_email='klaudia.adamowicz@uni-hamburg.de',
    url='http://pypi.python.org/pypi/biodigest/',
    license='LICENSE',
    description="In silico Validation of Disease and Gene Sets, Clusterings or Subnetworks (DIGEST)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['biodigest', 'biodigest.evaluation', 'biodigest.evaluation.d_utils', 'biodigest.evaluation.mappers'],
    classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: Science/Research',
        # "License :: OSI Approved :: MIT License",
        # "Operating System :: OS Independent",
    ],                                      # Information to filter the project on PyPi website
    python_requires='>=3.7',
    install_requires=[
        "pandas>=1.2.0",
        "numpy>=1.20.0",
        "scipy>=1.5.4",
        "seaborn==0.11.2",
        "biothings_client==0.2.6",
        "gseapy==0.10.5",
        "psutil==5.9.0",
        "requests>=2.26.0",
        "pycairo>=1.20.1",
    ]
)
