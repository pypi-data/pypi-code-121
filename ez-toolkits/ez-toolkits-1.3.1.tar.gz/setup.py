from setuptools import find_packages, setup

setup(
    name='ez-toolkits',
    version='1.3.1',
    author='septvean',
    author_email='septvean@gmail.com',
    description='Easy Toolkits',
    packages=find_packages(exclude=['tests']),
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        'matplotlib>=3.0.0',
        'pandas>=1.0.0',
        'requests>=2.0.0'
    ]
)
