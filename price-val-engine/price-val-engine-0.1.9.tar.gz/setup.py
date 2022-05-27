from setuptools import find_packages, setup
from os.path import join, dirname

with open(join(dirname(__file__), 'price_val_engine/VERSION'), 'rb') as f:
    version = f.read().decode('ascii').strip()

with open('README.md') as f:
    README = f.read()
    
setup(
    name='price-val-engine',
    packages=find_packages(),
    version=version,
    description='last price revision validation rules',
    long_description=README,
    long_description_content_type= 'text/markdown',
    author='Chandan Kumar Ojha',
    author_email="mr.chandanojha@gmail.com",
    include_package_data=True,
    license='MIT',
    python_requires=">=3.6",
    install_requires=[
        'boto3>=1.21.45',
        'botocore>=1.24.45',
        'fsspec>=2022.1.0',
        'slack_sdk>=3.16.2'
    ]
)