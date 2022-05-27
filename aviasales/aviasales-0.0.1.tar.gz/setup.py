from setuptools import setup

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name='aviasales',
    version='0.0.1',
    packages=['aviasales'],
    install_requires=['aiohttp', 'pydantic', 'faker', ],
    url='https://github.com/masterbpro/aviasales_api',
    license='MIT',
    author='akbarov',
    author_email='iserver12345@gmail.com',
    description='Pirate API for aviasales.ru',
    long_description=long_description,
    long_description_content_type="text/markdown",

)
