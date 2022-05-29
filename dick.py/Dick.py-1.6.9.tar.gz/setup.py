from setuptools import setup, find_packages

with open("README.md", "r") as stream:
    long_description = stream.read()

setup(
    name = 'Dick.py',
    version = '1.6.9',
    url = 'https://github.com/aminobot22/MAmino.py',
    download_url = 'https://github.com/aminobot22/MAmino.py.git',
    license = 'MIT',
    author = 'Slimakoi',
    author_email = 'slimeytoficial@gmail.com',
    description = 'A library to create Amino bots.',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    keywords = [
        'aminoapps',
        'Dick',
        'amino',
        'amino-bot',
        'narvii',
        'api',
        'python',
        'python3',
        'python3.x',
        'slimakoi',
        'official'
    ],
    install_requires = [
        'setuptools',
        'requests',
        'six',
        'websocket-client==0.57.0',
        'json_minify',
        'secmail',
        'bs4',
        'names',
        'requests-random-user-agent'
    ],
    setup_requires = [
        'wheel'
    ],
    packages = find_packages()
)
