from setuptools import setup, find_packages

with open("README.md", "r") as readme_file:
    readme = readme_file.read()

req = [
    'asn1crypto==1.5.1',
    'bleach==5.0.0',
    'certifi==2022.5.18.1',
    'cffi==1.15.0',
    'charset-normalizer==2.0.12',
    'coincurve==17.0.0',
    'commonmark==0.9.1',
    'cryptography==37.0.2',
    'docutils==0.18.1',
    'idna==3.3',
    'importlib-metadata==4.11.4',
    'jeepney==0.8.0',
    'keyring==23.5.1',
    'pkginfo==1.8.2',
    'pycparser==2.21',
    'Pygments==2.12.0',
    'pysha3==1.0.2',
    'readme-renderer==35.0',
    'requests==2.27.1',
    'requests-toolbelt==0.9.1',
    'rfc3986==2.0.0',
    'rich==12.4.4',
    'SecretStorage==3.3.2',
    'six==1.16.0',
    'twine==4.0.0',
    'typing_extensions==4.2.0',
    'urllib3==1.26.9',
    'webencodings==0.5.1',
    'zipp==3.8.0',
       ]

setup(
    name='AntFake',
    version='0.1.4',
    license='MIT',
    author="Inkviz96",
    author_email='b-semen-b@mail.ru',
    packages=find_packages(),
    url='https://github.com/inkviz96/antFake',
    keywords='fake test web3 eth',
    description="Ant is library for generation random string, float, eth address and pk, etc",
    long_description=readme,
    long_description_content_type="text/markdown",
    install_requires=req,
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
    ],
)