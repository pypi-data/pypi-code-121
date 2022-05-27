from setuptools import setup, find_packages

LONG_DESCRIPTION = open('README.md', 'r').read()

REQUIREMENTS = open('requirements.txt', 'r').read().split('\n')

setup(
    name='hashflow-python',
    version='10.7.0',
    packages=find_packages(),
    package_data={
        'hashflow': ['abi/*.json', 'deployed.json'],
    },
    description='Python SDK to interact with hashflow Smart Contracts',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    url='',
    author='H-Protocol Inc',
    license='Apache 2.0',
    author_email='varun@hashflow.com',
    install_requires=REQUIREMENTS,
    keywords='hashflow exchange api defi ethereum eth',
    classifiers=[],
)
