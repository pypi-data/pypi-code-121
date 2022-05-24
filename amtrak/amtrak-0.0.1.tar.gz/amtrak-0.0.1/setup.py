from setuptools import find_packages, setup

setup(
    name="amtrak",
    version="0.0.1",
    install_requires=[
        "cloudpickle>=2.0.0",
        "gcsfs>=2021.7.0",
        "python-configuration[yaml]~=0.8",
        "pandas>=1.0.0",  # vertex images are on 1.0.4
        "smart-open~=5.0",
    ],
    extras_require={"test": ["pytest==6.2.2", "pytest-env"]},
    packages=find_packages(include=["amtrak", "amtrak.**"]),
)
