#!/usr/bin/env python
#   -*- coding: utf-8 -*-

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'rincewindwizzard-example-cli',
        version = '0.0.1a',
        description = 'Example PyBuilder / Git project',
        long_description = 'An example command line tool',
        long_description_content_type = None,
        classifiers = [
            'Development Status :: 3 - Alpha',
            'Programming Language :: Python'
        ],
        keywords = '',

        author = 'RincewindWizzard',
        author_email = 'git@magierdinge.de',
        maintainer = '',
        maintainer_email = '',

        license = 'None',

        url = 'https://github.com/awwsmm/PybGit',
        project_urls = {},

        scripts = ['scripts/example-cli'],
        packages = ['example_cli'],
        namespace_packages = [],
        py_modules = [],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '',
        obsoletes = [],
    )
