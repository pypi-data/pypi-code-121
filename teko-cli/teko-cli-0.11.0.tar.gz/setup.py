from setuptools import setup, find_packages

with open('README.md') as readme_file:
    README = readme_file.read()

with open('HISTORY.md') as history_file:
    HISTORY = history_file.read()

setup_args = dict(
    name='teko-cli',
    version='0.11.0',
    description='Teko CLI tools',
    long_description_content_type="text/markdown",
    long_description=README + '\n\n' + HISTORY,
    license='MIT',
    packages=find_packages(exclude=('tests', )),
    include_package_data=True,
    author='Thuc Nguyen',
    author_email='thuc.nc@teko.vn',
    keywords=['Teko', 'Teko CLI tools'],
    url='https://git.teko.vn/vnpay-marketing-portal/teko-tools',
    download_url='https://pypi.org/project/teko/',
    entry_points='''
        [console_scripts]
        teko=teko.cli.main:app
    ''',
)

install_requires = [
    'requests',
    'jinja2',
    'tabulate',
    'typer',
    'colorama',
    'dataclasses-json',
    'ruamel.yaml',
    'python-dotenv',
    "bs4"
]


if __name__ == '__main__':
    setup(**setup_args, install_requires=install_requires)
