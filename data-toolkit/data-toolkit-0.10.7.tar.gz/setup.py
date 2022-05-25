
from setuptools import setup, find_packages
from dt.core.version import get_version

VERSION = get_version()

f = open('README.md', 'r')
LONG_DESCRIPTION = f.read()
f.close()

setup(
    name='data-toolkit',
    version=VERSION,
    description='ML & data helper code!',
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author='Jakub Langr',
    author_email='james.langr@gmail.com',
    url='https://github.com/johndoe/myapp/',
    license='(c) Jakub Langr',
    packages=find_packages(exclude=['ez_setup', 'tests*']),
    package_data={'dt': ['templates/*', 'dt/scripts/*']},
    data_files=[('',["dt/ext/zshrc.txt"])],
    include_package_data=True,
    python_requires='>=3.6',
    entry_points="""
        [console_scripts]
        dt = dt.main:main
    """,
    install_requires=[
        # 'sentry_sdk',
        'python-Levenshtein',
        'github3.py',
        'cement',
        'humanize',
        'jinja2',
        'pyyaml',
        'colorlog',
        'gputil',
    ]
)
