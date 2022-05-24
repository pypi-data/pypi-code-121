from setuptools import find_packages, setup

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setup(
    name='cryptcli',
    version='0.2.0',
    license='MIT',
    description='The cryptcli is a python package that gives you access to cryptocurrency prices right in your terminal!',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Aiden Olsen',
    author_email='olsenaiden33@gmail.com',
    url='https://github.com/AineeJames/cryptcli',
    download_url='https://github.com/AineeJames/cryptcli/releases/tag/v0.1.0',
    keywords=['crypto', 'cli', 'plot'],
    packages=find_packages(),
    install_requires=[
        'typer',
        'rich',
        'plotext',
        'inquirer',
    ],
    entry_points='''
    [console_scripts]
    crypt=cryptcli:app
    ''',
)

print("setup")
