import setuptools

# Load README
with open('README.md', 'r', encoding = 'utf8') as file:
    long_description = file.read()

# Define package metadata
setuptools.setup(
    name = 'sitzungsdienst',
    version = '2.0.0',
    author = 'Martin Folkers',
    author_email = 'hello@twobrain.io',
    description = 'A simple Python utility for working with weekly assignment PDFs as exported by "web.sta"',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://codeberg.org/S1SYPHOS/sitzungsdienst',
    license = 'MIT',
    project_urls = {
        'Issues': 'https://codeberg.org/S1SYPHOS/sitzungsdienst/issues',
    },
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    packages = setuptools.find_packages(),
    install_requires = [
        'backports.zoneinfo; python_version < "3.10"',
        'ics',
        'pypdf2',
        'pytest',
    ],
    python_requires = '>= 3.7'
)
