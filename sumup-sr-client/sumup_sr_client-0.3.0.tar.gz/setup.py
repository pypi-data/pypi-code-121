from setuptools import setup

setup(
    name='sumup_sr_client',
    version='0.3.0',
    description='A Python Package for the sumup schema registry client',
    author='Ajay Muppuri',
    author_email='ajay.muppuri@sumup.com',
    packages=['schema_registry', 'schema_registry.client', 'schema_registry.registry', 'schema_registry.utils'],
    install_requires=['acryl-datahub[kafka]'
                      ]
)
download_url="https://github.com/sumup/data-ingestion-infrastructure/archive/refs/tags/0.1.0.tar.gz"