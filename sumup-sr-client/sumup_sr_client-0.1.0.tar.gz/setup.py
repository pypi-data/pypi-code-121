from setuptools import setup

setup(
    name='sumup_sr_client',
    version='0.1.0',
    description='A Python Package for the sumup schema registry client',
    author='Ajay Muppuri',
    author_email='ajay.muppuri@sumup.com',
    packages=['src'],
    install_requires=['acryl-datahub[kafka]'
                      ]
)
