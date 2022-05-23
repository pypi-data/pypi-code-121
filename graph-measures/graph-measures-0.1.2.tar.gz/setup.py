from setuptools import setup, find_packages

setup(
    name='graph-measures',
    version='0.1.2',
    license='GPL',
    maintainer="Amit Kabya",
    author="Itay Levinas, Roy Sh",
    author_email='kabya.amit@gmail.com',
    packages=find_packages(),
    url='https://github.com/louzounlab/graph-measures',
    description='A python package for calculating topological graph features on cpu/gpu',
    keywords='gpu graph topological-features-calculator',
    install_requires=[
        "setuptools<=61.3.1",
        "networkx<=2.8",
        "pandas<=1.4.2",
        "numpy<=1.22.3",
        "matplotlib<=3.5.1",
        "scipy<=1.8.0",
        "scikit-learn<=1.0.2",
        "python-louvain<=0.16",
        "bitstring<=3.1.9"
    ],

)
