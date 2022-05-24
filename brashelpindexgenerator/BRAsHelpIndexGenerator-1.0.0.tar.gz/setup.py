from setuptools import setup

setup(
    name='BRAsHelpIndexGenerator',
    version='1.0.0',
    packages=['brAsHelpIndexGenerator'],
    url='https://github.com/br-na-pm/mkdocs-as-help-index-generator',
    license='GPL-3',
    author='Connor Trostel',
    author_email='connor.trostel@br-automation.com',
    include_package_data=True,
    long_description='AS Help Index Generator is a tool to generate the xml index files needed for a documentation site generated from MkDocs to work in the AS Help.',
    install_requires=['mkdocs'],

    entry_points={
        'mkdocs.plugins': [
            'br-as-help-index-gen = brAsHelpIndexGenerator:BrAsHelpIndexGenerator',
        ]
    },
)
