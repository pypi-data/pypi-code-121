import os
from setuptools import find_packages, setup

##
# @file
# @brief This setup.py file is used for creating a Pkg from the ds-framework.
#        In order to be able to pip install ds-framework.

with open('requirements.txt') as f:
    required = f.read().splitlines()


def package_files(directory):
    paths = []
    for (path, directories, filenames) in os.walk(directory):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()


dsp_files = package_files('dsframework/cli/tester/dsp')
extra_files = package_files('dsframework/cli/tester/deploy_files')
cloud_eval_extra_files = package_files('dsframework/cli/tester/cloud_eval')
batch_extra_files = package_files('dsframework/cli/tester/batch_files')
documentation_files = package_files('dsframework/documentation')

setup(
    name='dsFramework',
    py_modules=['api_cli'],

    packages=find_packages(include=['dsframework*']),
    package_data={'': ['config.json', 'cors_allowed_origins.json', '.gitignore'] +
                      extra_files + cloud_eval_extra_files + dsp_files + documentation_files + batch_extra_files},
    entry_points='''
        [console_scripts]
        dsf-cli=api_cli:cli
    ''',
    version='0.1.91',
    description='Data science framework library',
    long_description=read('README.md'),
    long_description_content_type='text/markdown',
    # url='http://pypi.python.org/pypi/PackageName/',
    author='oribrau@gmail.com',
    license='MIT',
    install_requires=required,
    setup_requires=['pytest-runner'],
    tests_require=['pytest'],
    test_suite='tests',
)

# Commands
# for test -  python setup.py pytest
# for build wheel -  python setup.py bdist_wheel
# for source dist -  python setup.py sdist
# for build -  python setup.py build
# for install -  python setup.py install
# for uninstall - python -m pip uninstall dsframework
# for install - python -m pip install dist/dsframework-0.1.0-py3-none-any.whl
# for installing from the local work dir - pip install <path to local directory>

# Deploy to PyPI
# delete dist and build folders
# python setup.py bdist_wheel
# python setup.py sdist
# python setup.py build
# twine upload dist/*
'''
    use
    1. python setup.py install
    2. dsf-cli g model new_model_name
    3. twine check dist/*
    4. twine upload --repository-url https://pypi.org/legacy/ dist/*
    4. twine upload dist/*
    
    pip install dsframework --index-url https://pypi.org/simple
    
    how to use
    
    pip install dsframework
    
    dsf-cli generate project my-new-model
'''
