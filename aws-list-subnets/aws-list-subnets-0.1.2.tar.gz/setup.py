from setuptools import setup, find_packages

with open('requirements.txt') as requirements_file:
    install_requirements = requirements_file.read().splitlines()

setup(
    name        = 'aws-list-subnets',
    version     = '0.1.2',
    description = "list aws subnets",
    author      = "suzuki-navi",
    packages    = find_packages(),
    install_requires = install_requirements,
    include_package_data = True,
    entry_points = {
        "console_scripts": [
            "aws-list-subnets = aws_list_subnets.main:main",
        ]
    },
)
