from setuptools import setup, find_packages

with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()

setup(
    name        = 'yamlist',
    version     = '0.0.0',
    description = "yamlist",
    author      = "suzuki-navi",
    packages    = find_packages(),
    install_requires = install_requirements,
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "yamlist = yamlist.main:main",
        ]
    },
)
