from setuptools import find_packages, setup

setup(
    name='cryptcli',
    version='0.1.0',
    license='MIT',
    description='The cryptcli is a python package that gives you access to cryptocurrency prices right in your terminal!',
    author='Aiden Olsen',
    author_email='olsenaiden33@gmail.com',
    url='https://github.com/AineeJames/cryptcli',
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
