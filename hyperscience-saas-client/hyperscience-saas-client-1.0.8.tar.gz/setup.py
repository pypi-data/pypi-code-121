from setuptools import find_packages, setup

from hyperscience._version import __version__ as version

SAAS_CLIENT_VERSION = version
PACKAGE_NAME = 'hyperscience-saas-client'

EXTRAS = {}

with open('dev-requirements.txt') as f:
    SETUP_REQUIRES = f.readlines()

REQUIRES = []
with open('requirements.txt') as f:
    for line in f:
        line, _, _ = line.partition('#')
        line = line.strip()
        if ';' in line:
            requirement, _, specifier = line.partition(';')
            for_specifier = EXTRAS.setdefault(':{}'.format(specifier), [])
            for_specifier.append(requirement)
        else:
            REQUIRES.append(line)

TESTS_REQUIRES = []
# with open('test-requirements.txt') as f:
#     TESTS_REQUIRES = f.readlines()

with open('README.md', encoding='utf-8') as f:
    readme = f.read()

setup(
    name=PACKAGE_NAME,
    packages=find_packages(exclude=['tests', 'samples', 'linters']),
    include_package_data=True,
    version=SAAS_CLIENT_VERSION,
    description='hyperscience saas client library',
    long_description=readme,
    long_description_content_type='text/markdown',
    author='Hyperscience',
    python_requires=">=3.6",
    # url should point to our public repository once created
    # url='https://gitlab.int.hyperscience.net/third-party-integrations/hyperscience-sdk/hyperscience-saas-client-python',
    license='Apache License 2.0',
    install_requires=REQUIRES,
    extras_require=EXTRAS,
    setup_requires=SETUP_REQUIRES,
    tests_require=TESTS_REQUIRES,
)
