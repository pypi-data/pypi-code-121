import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='phased_methylation',
    version='0.17.5',
    author='Anthony Aylward, Brad Abramson, Nolan Hartwick',
    author_email='aaylward@salk.edu',
    description='Pipeline for phased methylation calling on raw nanopore data',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://gitlab.com/salk-tm/phased-methylation',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
    install_requires=['cython', 'pandas', 'pysam', 'pybedtools', 'pyfaidx',
                      'megalodon', 'GPUtil', 'nvsmi', 'psutil', 'tabulate',
                      'tempfifo'],
    entry_points={
        'console_scripts': [
            'phased-methylation=phased_methylation.phased_methylation:main',
            'split-methyl-bed=phase_methylation.split_methyl_bed:main'
        ]
    },
    include_package_data=True
)
