#!/usr/bin/env python3
import os
from setuptools import setup

BASEDIR = os.path.abspath(os.path.dirname(__file__))


def required(requirements_file):
    """ Read requirements file and remove comments and empty lines. """
    with open(os.path.join(BASEDIR, requirements_file), 'r') as f:
        requirements = f.read().splitlines()
        if 'MYCROFT_LOOSE_REQUIREMENTS' in os.environ:
            print('USING LOOSE REQUIREMENTS!')
            requirements = [r.replace('==', '>=').replace('~=', '>=') for r in requirements]
        return [pkg for pkg in requirements
                if pkg.strip() and not pkg.startswith("#")]


with open("README.md", "r") as f:
    long_description = f.read()


PLUGIN_ENTRY_POINT = 'neon_solver_ddg_plugin=neon_solver_ddg_plugin:DDGSolver'
setup(
    name='neon_solver_ddg_plugin',
    version='0.0.0a0',
    description='A question solver plugin for ovos/neon/mycroft',
    url='https://github.com/NeonGeckoCom/neon_solver_ddg_plugin',
    author='Neongecko',
    author_email='developers@neon.ai',
    license='bsd3',
    install_requires=required("requirements/requirements.txt"),
    packages=['neon_solver_ddg_plugin'],
    zip_safe=True,
    keywords='mycroft plugin utterance fallback query',
    entry_points={'neon.plugin.solver': PLUGIN_ENTRY_POINT},
    long_description=long_description,
    long_description_content_type='text/markdown'
)
