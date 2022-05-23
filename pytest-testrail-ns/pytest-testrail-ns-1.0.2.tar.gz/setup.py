from setuptools import setup


def read_file(fname):
    with open(fname) as f:
        return f.read()


setup(
    name='pytest-testrail-ns',
    description='pytest plugin for creating TestRail runs and adding results',
    long_description=read_file('README.rst'),
    version='1.0.2',
    author='NGUYEN Viet',
    author_email='vietnq254@live.com',
    url='https://github.com/nishithcitc/pytest-testrail-ns',
    packages=[
        'pytest_testrail',
    ],
    package_dir={'pytest_testrail_ns': 'pytest_testrail_ns'},
    install_requires=[
        'pytest>=3.6',
        'requests>=2.20.0',
    ],
    include_package_data=True,
    entry_points={'pytest11': ['pytest-testrail-ns = pytest_testrail.conftest']},
)
