from setuptools import find_packages, setup

with open("README.md") as file:
    long_description = file.read()

setup(
    name='dsgl',
    packages=find_packages(include=['dsgl']),
    version='0.1.0',
    description='Library consisting of DS shortcuts and best practice functions for the Globallogic Datascience team',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='DS GL Team',
    license='MIT',
    install_requires=[],
    keywords=["python","data","science","globallogic"],
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)
