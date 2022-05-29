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
        name = 'pybuilder',
        version = '0.13.6',
        description = 'PyBuilder — an easy-to-use build automation tool for Python.',
        long_description = '[PyBuilder &#x2014; an easy-to-use build automation tool for Python](https://pybuilder.io)\n=========\n\n[![Follow PyBuilder on Twitter](https://img.shields.io/twitter/follow/pybuilder_?label=Follow%20PyBuilder&style=social)](https://twitter.com/intent/follow?screen_name=pybuilder_)\n[![Gitter](https://img.shields.io/gitter/room/pybuilder/pybuilder?logo=gitter)](https://gitter.im/pybuilder/pybuilder)\n[![Build Status](https://img.shields.io/github/workflow/status/pybuilder/pybuilder/pybuilder/master)](https://github.com/pybuilder/pybuilder/actions/workflows/pybuilder.yml)\n[![Coverage Status](https://img.shields.io/coveralls/github/pybuilder/pybuilder/master?logo=coveralls)](https://coveralls.io/r/pybuilder/pybuilder?branch=master)\n\n[![PyBuilder Version](https://img.shields.io/pypi/v/pybuilder?logo=pypi)](https://pypi.org/project/pybuilder/)\n[![PyBuilder Python Versions](https://img.shields.io/pypi/pyversions/pybuilder?logo=pypi)](https://pypi.org/project/pybuilder/)\n[![PyBuilder Downloads Per Day](https://img.shields.io/pypi/dd/pybuilder?logo=pypi)](https://pypi.org/project/pybuilder/)\n[![PyBuilder Downloads Per Week](https://img.shields.io/pypi/dw/pybuilder?logo=pypi)](https://pypi.org/project/pybuilder/)\n[![PyBuilder Downloads Per Month](https://img.shields.io/pypi/dm/pybuilder?logo=pypi)](https://pypi.org/project/pybuilder/)\n\nPyBuilder is a software build tool written in 100% pure Python, mainly\ntargeting Python applications.\n\nPyBuilder is based on the concept of dependency based programming, but it also\ncomes with a powerful plugin mechanism, allowing the construction of build life\ncycles similar to those known from other famous (Java) build tools.\n\nPyBuilder is running on the following versions of Python 3.6, 3.7, 3.8, 3.9, 3.10, and PyPy 3.7.\n\nSee the [GitHub Actions Workflow](https://github.com/pybuilder/pybuilder/actions/workflows/pybuilder.yml) for version specific output.\n\n## Installing\n\nPyBuilder is available using pip:\n\n    $ pip install pybuilder\n\nFor development builds use:\n\n    $ pip install --pre pybuilder\n\nSee the [PyPI](https://pypi.org/project/pybuilder/) for more information.\n\n## Getting started\n\nPyBuilder emphasizes simplicity. If you want to build a pure Python project and\nuse the recommended directory layout, all you have to do is create a file\nbuild.py with the following content:\n\n```python\nfrom pybuilder.core import use_plugin\n\nuse_plugin("python.core")\nuse_plugin("python.unittest")\nuse_plugin("python.coverage")\nuse_plugin("python.distutils")\n\ndefault_task = "publish"\n```\n\nSee the [PyBuilder homepage](https://pybuilder.io) for more details and\na list of plugins.\n\n## Release Notes\n\nThe release notes can be found [here](https://pybuilder.io/release-notes/).\nThere will also be a git tag with each release. Please note that we do not currently promote tags to GitHub "releases".\n\n## Development\nSee [Developing PyBuilder](https://pybuilder.io/documentation/developing-pybuilder)\n',
        long_description_content_type = 'text/markdown',
        classifiers = [
            'Programming Language :: Python',
            'Programming Language :: Python :: Implementation :: CPython',
            'Programming Language :: Python :: Implementation :: PyPy',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Programming Language :: Python :: 3.9',
            'Programming Language :: Python :: 3.10',
            'Operating System :: MacOS :: MacOS X',
            'Operating System :: POSIX :: Linux',
            'Operating System :: Microsoft :: Windows',
            'Operating System :: OS Independent',
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Topic :: Software Development :: Build Tools',
            'Topic :: Software Development :: Quality Assurance',
            'Topic :: Software Development :: Testing'
        ],
        keywords = 'PyBuilder PyB build tool automation Python testing QA packaging distribution',

        author = 'Arcadiy Ivanov, Alexander Metzner, Maximilien Riehl, Michael Gruber, Udo Juettner, Marcel Wolf, Valentin Haenel',
        author_email = 'arcadiy@ivanov.biz, alexander.metzner@gmail.com, max@riehl.io, aelgru@gmail.com, udo.juettner@gmail.com, marcel.wolf@me.com, valentin@haenel.co',
        maintainer = 'Arcadiy Ivanov',
        maintainer_email = 'arcadiy@ivanov.biz',

        license = 'Apache License, Version 2.0',

        url = 'https://pybuilder.io',
        project_urls = {
            'Bug Tracker': 'https://github.com/pybuilder/pybuilder/issues',
            'Documentation': 'https://pybuilder.io/documentation',
            'Source Code': 'https://github.com/pybuilder/pybuilder',
            'Twitter': 'https://twitter.com/pybuilder_'
        },

        scripts = ['scripts/pyb'],
        packages = [
            'pybuilder',
            'pybuilder._vendor',
            'pybuilder._vendor._distutils_hack',
            'pybuilder._vendor.colorama',
            'pybuilder._vendor.distlib',
            'pybuilder._vendor.filelock',
            'pybuilder._vendor.importlib_metadata',
            'pybuilder._vendor.importlib_resources',
            'pybuilder._vendor.importlib_resources.tests',
            'pybuilder._vendor.importlib_resources.tests.data01',
            'pybuilder._vendor.importlib_resources.tests.data01.subdirectory',
            'pybuilder._vendor.importlib_resources.tests.data02',
            'pybuilder._vendor.importlib_resources.tests.data02.one',
            'pybuilder._vendor.importlib_resources.tests.data02.two',
            'pybuilder._vendor.importlib_resources.tests.zipdata01',
            'pybuilder._vendor.importlib_resources.tests.zipdata02',
            'pybuilder._vendor.pkg_resources',
            'pybuilder._vendor.pkg_resources._vendor',
            'pybuilder._vendor.pkg_resources._vendor.importlib_resources',
            'pybuilder._vendor.pkg_resources._vendor.jaraco',
            'pybuilder._vendor.pkg_resources._vendor.jaraco.text',
            'pybuilder._vendor.pkg_resources._vendor.more_itertools',
            'pybuilder._vendor.pkg_resources._vendor.packaging',
            'pybuilder._vendor.pkg_resources.extern',
            'pybuilder._vendor.platformdirs',
            'pybuilder._vendor.tailer',
            'pybuilder._vendor.tblib',
            'pybuilder._vendor.virtualenv',
            'pybuilder._vendor.virtualenv.activation',
            'pybuilder._vendor.virtualenv.activation.bash',
            'pybuilder._vendor.virtualenv.activation.batch',
            'pybuilder._vendor.virtualenv.activation.cshell',
            'pybuilder._vendor.virtualenv.activation.fish',
            'pybuilder._vendor.virtualenv.activation.nushell',
            'pybuilder._vendor.virtualenv.activation.powershell',
            'pybuilder._vendor.virtualenv.activation.python',
            'pybuilder._vendor.virtualenv.app_data',
            'pybuilder._vendor.virtualenv.config',
            'pybuilder._vendor.virtualenv.config.cli',
            'pybuilder._vendor.virtualenv.create',
            'pybuilder._vendor.virtualenv.create.via_global_ref',
            'pybuilder._vendor.virtualenv.create.via_global_ref.builtin',
            'pybuilder._vendor.virtualenv.create.via_global_ref.builtin.cpython',
            'pybuilder._vendor.virtualenv.create.via_global_ref.builtin.pypy',
            'pybuilder._vendor.virtualenv.create.via_global_ref.builtin.python2',
            'pybuilder._vendor.virtualenv.discovery',
            'pybuilder._vendor.virtualenv.discovery.windows',
            'pybuilder._vendor.virtualenv.run',
            'pybuilder._vendor.virtualenv.run.plugin',
            'pybuilder._vendor.virtualenv.seed',
            'pybuilder._vendor.virtualenv.seed.embed',
            'pybuilder._vendor.virtualenv.seed.embed.via_app_data',
            'pybuilder._vendor.virtualenv.seed.embed.via_app_data.pip_install',
            'pybuilder._vendor.virtualenv.seed.wheels',
            'pybuilder._vendor.virtualenv.seed.wheels.embed',
            'pybuilder._vendor.virtualenv.util',
            'pybuilder._vendor.virtualenv.util.path',
            'pybuilder._vendor.virtualenv.util.path._pathlib',
            'pybuilder._vendor.virtualenv.util.subprocess',
            'pybuilder.extern',
            'pybuilder.pluginhelper',
            'pybuilder.plugins',
            'pybuilder.plugins.python',
            'pybuilder.plugins.python.remote_tools',
            'pybuilder.remote'
        ],
        namespace_packages = [],
        py_modules = [],
        entry_points = {
            'console_scripts': ['pyb = pybuilder.cli:main']
        },
        data_files = [],
        package_data = {
            'pybuilder': ['LICENSE'],
            'pybuilder._vendor': ['zipp.py', 'LICENSES', '__init__.py', 'six.py', 'typing_extensions.py', 'tailer/__init__.py', 'importlib_metadata-4.11.1.dist-info/INSTALLER', 'importlib_metadata-4.11.1.dist-info/LICENSE', 'importlib_metadata-4.11.1.dist-info/REQUESTED', 'importlib_metadata-4.11.1.dist-info/top_level.txt', 'importlib_metadata-4.11.1.dist-info/RECORD', 'importlib_metadata-4.11.1.dist-info/METADATA', 'importlib_metadata-4.11.1.dist-info/WHEEL', 'tblib/decorators.py', 'tblib/pickling_support.py', 'tblib/__init__.py', 'tblib/cpython.py', 'tblib/__pycache__/cpython.cpython-310.pyc', 'tblib/__pycache__/__init__.cpython-310.pyc', 'tblib/__pycache__/pickling_support.cpython-310.pyc', '_distutils_hack/__init__.py', '_distutils_hack/override.py', '_distutils_hack/__pycache__/__init__.cpython-310.pyc', '_distutils_hack/__pycache__/override.cpython-310.pyc', 'platformdirs/android.py', 'platformdirs/macos.py', 'platformdirs/__main__.py', 'platformdirs/py.typed', 'platformdirs/unix.py', 'platformdirs/api.py', 'platformdirs/__init__.py', 'platformdirs/version.py', 'platformdirs/windows.py', 'platformdirs/__pycache__/__init__.cpython-310.pyc', 'platformdirs/__pycache__/unix.cpython-310.pyc', 'platformdirs/__pycache__/version.cpython-310.pyc', 'platformdirs/__pycache__/api.cpython-310.pyc', 'colorama/ansitowin32.py', 'colorama/initialise.py', 'colorama/ansi.py', 'colorama/win32.py', 'colorama/__init__.py', 'colorama/winterm.py', 'pkg_resources/__init__.py', 'pkg_resources/_vendor/pyparsing.py', 'pkg_resources/_vendor/zipp.py', 'pkg_resources/_vendor/appdirs.py', 'pkg_resources/_vendor/__init__.py', 'pkg_resources/_vendor/more_itertools/more.py', 'pkg_resources/_vendor/more_itertools/recipes.py', 'pkg_resources/_vendor/more_itertools/__init__.py', 'pkg_resources/_vendor/importlib_resources/_common.py', 'pkg_resources/_vendor/importlib_resources/abc.py', 'pkg_resources/_vendor/importlib_resources/_itertools.py', 'pkg_resources/_vendor/importlib_resources/readers.py', 'pkg_resources/_vendor/importlib_resources/simple.py', 'pkg_resources/_vendor/importlib_resources/__init__.py', 'pkg_resources/_vendor/importlib_resources/_compat.py', 'pkg_resources/_vendor/importlib_resources/_legacy.py', 'pkg_resources/_vendor/importlib_resources/_adapters.py', 'pkg_resources/_vendor/packaging/markers.py', 'pkg_resources/_vendor/packaging/requirements.py', 'pkg_resources/_vendor/packaging/specifiers.py', 'pkg_resources/_vendor/packaging/_musllinux.py', 'pkg_resources/_vendor/packaging/_manylinux.py', 'pkg_resources/_vendor/packaging/__about__.py', 'pkg_resources/_vendor/packaging/__init__.py', 'pkg_resources/_vendor/packaging/utils.py', 'pkg_resources/_vendor/packaging/_structures.py', 'pkg_resources/_vendor/packaging/tags.py', 'pkg_resources/_vendor/packaging/version.py', 'pkg_resources/_vendor/packaging/__pycache__/_structures.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/__init__.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/utils.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/markers.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/specifiers.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/__about__.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/version.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/_musllinux.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/tags.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/_manylinux.cpython-310.pyc', 'pkg_resources/_vendor/packaging/__pycache__/requirements.cpython-310.pyc', 'pkg_resources/_vendor/jaraco/context.py', 'pkg_resources/_vendor/jaraco/functools.py', 'pkg_resources/_vendor/jaraco/__init__.py', 'pkg_resources/_vendor/jaraco/__pycache__/context.cpython-310.pyc', 'pkg_resources/_vendor/jaraco/__pycache__/__init__.cpython-310.pyc', 'pkg_resources/_vendor/jaraco/__pycache__/functools.cpython-310.pyc', 'pkg_resources/_vendor/jaraco/text/__init__.py', 'pkg_resources/_vendor/jaraco/text/__pycache__/__init__.cpython-310.pyc', 'pkg_resources/_vendor/__pycache__/appdirs.cpython-310.pyc', 'pkg_resources/_vendor/__pycache__/pyparsing.cpython-310.pyc', 'pkg_resources/_vendor/__pycache__/__init__.cpython-310.pyc', 'pkg_resources/extern/__init__.py', 'pkg_resources/extern/__pycache__/__init__.cpython-310.pyc', 'pkg_resources/__pycache__/__init__.cpython-310.pyc', 'importlib_resources/_common.py', 'importlib_resources/abc.py', 'importlib_resources/_itertools.py', 'importlib_resources/py.typed', 'importlib_resources/readers.py', 'importlib_resources/simple.py', 'importlib_resources/__init__.py', 'importlib_resources/_compat.py', 'importlib_resources/_legacy.py', 'importlib_resources/_adapters.py', 'importlib_resources/tests/test_compatibilty_files.py', 'importlib_resources/tests/test_files.py', 'importlib_resources/tests/util.py', 'importlib_resources/tests/test_path.py', 'importlib_resources/tests/test_open.py', 'importlib_resources/tests/__init__.py', 'importlib_resources/tests/test_read.py', 'importlib_resources/tests/test_reader.py', 'importlib_resources/tests/_compat.py', 'importlib_resources/tests/test_contents.py', 'importlib_resources/tests/test_resource.py', 'importlib_resources/tests/update-zips.py', 'importlib_resources/tests/data01/binary.file', 'importlib_resources/tests/data01/utf-8.file', 'importlib_resources/tests/data01/utf-16.file', 'importlib_resources/tests/data01/__init__.py', 'importlib_resources/tests/data01/subdirectory/binary.file', 'importlib_resources/tests/data01/subdirectory/__init__.py', 'importlib_resources/tests/zipdata02/ziptestdata.zip', 'importlib_resources/tests/zipdata02/__init__.py', 'importlib_resources/tests/namespacedata01/binary.file', 'importlib_resources/tests/namespacedata01/utf-8.file', 'importlib_resources/tests/namespacedata01/utf-16.file', 'importlib_resources/tests/zipdata01/ziptestdata.zip', 'importlib_resources/tests/zipdata01/__init__.py', 'importlib_resources/tests/data02/__init__.py', 'importlib_resources/tests/data02/two/__init__.py', 'importlib_resources/tests/data02/two/resource2.txt', 'importlib_resources/tests/data02/one/__init__.py', 'importlib_resources/tests/data02/one/resource1.txt', '__pycache__/__init__.cpython-310.pyc', '__pycache__/six.cpython-310.pyc', 'virtualenv-20.13.1.dist-info/entry_points.txt', 'virtualenv-20.13.1.dist-info/INSTALLER', 'virtualenv-20.13.1.dist-info/LICENSE', 'virtualenv-20.13.1.dist-info/REQUESTED', 'virtualenv-20.13.1.dist-info/zip-safe', 'virtualenv-20.13.1.dist-info/top_level.txt', 'virtualenv-20.13.1.dist-info/RECORD', 'virtualenv-20.13.1.dist-info/METADATA', 'virtualenv-20.13.1.dist-info/WHEEL', 'distlib/database.py', 'distlib/wheel.py', 'distlib/resources.py', 'distlib/t64-arm.exe', 'distlib/markers.py', 'distlib/w64.exe', 'distlib/util.py', 'distlib/metadata.py', 'distlib/locators.py', 'distlib/manifest.py', 'distlib/compat.py', 'distlib/index.py', 'distlib/w64-arm.exe', 'distlib/t64.exe', 'distlib/__init__.py', 'distlib/w32.exe', 'distlib/scripts.py', 'distlib/t32.exe', 'distlib/version.py', 'distlib/__pycache__/resources.cpython-310.pyc', 'distlib/__pycache__/__init__.cpython-310.pyc', 'distlib/__pycache__/compat.cpython-310.pyc', 'distlib/__pycache__/util.cpython-310.pyc', 'distlib/__pycache__/scripts.cpython-310.pyc', 'filelock/_unix.py', 'filelock/_soft.py', 'filelock/_error.py', 'filelock/py.typed', 'filelock/_api.py', 'filelock/__init__.py', 'filelock/_util.py', 'filelock/_windows.py', 'filelock/version.py', 'filelock/__pycache__/_error.cpython-310.pyc', 'filelock/__pycache__/_unix.cpython-310.pyc', 'filelock/__pycache__/_api.cpython-310.pyc', 'filelock/__pycache__/__init__.cpython-310.pyc', 'filelock/__pycache__/_util.cpython-310.pyc', 'filelock/__pycache__/_windows.cpython-310.pyc', 'filelock/__pycache__/version.cpython-310.pyc', 'filelock/__pycache__/_soft.cpython-310.pyc', 'importlib_metadata/_functools.py', 'importlib_metadata/_itertools.py', 'importlib_metadata/py.typed', 'importlib_metadata/__init__.py', 'importlib_metadata/_compat.py', 'importlib_metadata/_collections.py', 'importlib_metadata/_meta.py', 'importlib_metadata/_text.py', 'importlib_metadata/_adapters.py', 'virtualenv/info.py', 'virtualenv/__main__.py', 'virtualenv/__init__.py', 'virtualenv/report.py', 'virtualenv/version.py', 'virtualenv/discovery/py_spec.py', 'virtualenv/discovery/py_info.py', 'virtualenv/discovery/__init__.py', 'virtualenv/discovery/builtin.py', 'virtualenv/discovery/cached_py_info.py', 'virtualenv/discovery/discover.py', 'virtualenv/discovery/__pycache__/__init__.cpython-310.pyc', 'virtualenv/discovery/__pycache__/py_spec.cpython-310.pyc', 'virtualenv/discovery/__pycache__/cached_py_info.cpython-310.pyc', 'virtualenv/discovery/__pycache__/discover.cpython-310.pyc', 'virtualenv/discovery/__pycache__/py_info.cpython-310.pyc', 'virtualenv/discovery/__pycache__/builtin.cpython-310.pyc', 'virtualenv/discovery/windows/pep514.py', 'virtualenv/discovery/windows/__init__.py', 'virtualenv/activation/activator.py', 'virtualenv/activation/via_template.py', 'virtualenv/activation/__init__.py', 'virtualenv/activation/cshell/activate.csh', 'virtualenv/activation/cshell/__init__.py', 'virtualenv/activation/cshell/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/python/activate_this.py', 'virtualenv/activation/python/__init__.py', 'virtualenv/activation/python/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/batch/activate.bat', 'virtualenv/activation/batch/deactivate.bat', 'virtualenv/activation/batch/pydoc.bat', 'virtualenv/activation/batch/__init__.py', 'virtualenv/activation/batch/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/nushell/deactivate.nu', 'virtualenv/activation/nushell/__init__.py', 'virtualenv/activation/nushell/activate.nu', 'virtualenv/activation/nushell/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/__pycache__/activator.cpython-310.pyc', 'virtualenv/activation/__pycache__/via_template.cpython-310.pyc', 'virtualenv/activation/powershell/activate.ps1', 'virtualenv/activation/powershell/__init__.py', 'virtualenv/activation/powershell/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/bash/activate.sh', 'virtualenv/activation/bash/__init__.py', 'virtualenv/activation/bash/__pycache__/__init__.cpython-310.pyc', 'virtualenv/activation/fish/__init__.py', 'virtualenv/activation/fish/activate.fish', 'virtualenv/activation/fish/__pycache__/__init__.cpython-310.pyc', 'virtualenv/app_data/na.py', 'virtualenv/app_data/via_disk_folder.py', 'virtualenv/app_data/via_tempdir.py', 'virtualenv/app_data/read_only.py', 'virtualenv/app_data/__init__.py', 'virtualenv/app_data/base.py', 'virtualenv/app_data/__pycache__/__init__.cpython-310.pyc', 'virtualenv/app_data/__pycache__/via_tempdir.cpython-310.pyc', 'virtualenv/app_data/__pycache__/na.cpython-310.pyc', 'virtualenv/app_data/__pycache__/base.cpython-310.pyc', 'virtualenv/app_data/__pycache__/read_only.cpython-310.pyc', 'virtualenv/app_data/__pycache__/via_disk_folder.cpython-310.pyc', 'virtualenv/seed/seeder.py', 'virtualenv/seed/__init__.py', 'virtualenv/seed/embed/base_embed.py', 'virtualenv/seed/embed/__init__.py', 'virtualenv/seed/embed/pip_invoke.py', 'virtualenv/seed/embed/via_app_data/via_app_data.py', 'virtualenv/seed/embed/via_app_data/__init__.py', 'virtualenv/seed/embed/via_app_data/pip_install/symlink.py', 'virtualenv/seed/embed/via_app_data/pip_install/copy.py', 'virtualenv/seed/embed/via_app_data/pip_install/__init__.py', 'virtualenv/seed/embed/via_app_data/pip_install/base.py', 'virtualenv/seed/embed/via_app_data/pip_install/__pycache__/symlink.cpython-310.pyc', 'virtualenv/seed/embed/via_app_data/pip_install/__pycache__/__init__.cpython-310.pyc', 'virtualenv/seed/embed/via_app_data/pip_install/__pycache__/base.cpython-310.pyc', 'virtualenv/seed/embed/via_app_data/pip_install/__pycache__/copy.cpython-310.pyc', 'virtualenv/seed/embed/via_app_data/__pycache__/__init__.cpython-310.pyc', 'virtualenv/seed/embed/via_app_data/__pycache__/via_app_data.cpython-310.pyc', 'virtualenv/seed/embed/__pycache__/__init__.cpython-310.pyc', 'virtualenv/seed/embed/__pycache__/base_embed.cpython-310.pyc', 'virtualenv/seed/embed/__pycache__/pip_invoke.cpython-310.pyc', 'virtualenv/seed/wheels/util.py', 'virtualenv/seed/wheels/acquire.py', 'virtualenv/seed/wheels/bundle.py', 'virtualenv/seed/wheels/__init__.py', 'virtualenv/seed/wheels/periodic_update.py', 'virtualenv/seed/wheels/embed/pip-22.0.3-py3-none-any.whl', 'virtualenv/seed/wheels/embed/pip-21.3.1-py3-none-any.whl', 'virtualenv/seed/wheels/embed/wheel-0.37.1-py2.py3-none-any.whl', 'virtualenv/seed/wheels/embed/setuptools-60.6.0-py3-none-any.whl', 'virtualenv/seed/wheels/embed/setuptools-50.3.2-py3-none-any.whl', 'virtualenv/seed/wheels/embed/setuptools-59.6.0-py3-none-any.whl', 'virtualenv/seed/wheels/embed/setuptools-44.1.1-py2.py3-none-any.whl', 'virtualenv/seed/wheels/embed/__init__.py', 'virtualenv/seed/wheels/embed/pip-20.3.4-py2.py3-none-any.whl', 'virtualenv/seed/wheels/embed/__pycache__/__init__.cpython-310.pyc', 'virtualenv/seed/wheels/__pycache__/acquire.cpython-310.pyc', 'virtualenv/seed/wheels/__pycache__/__init__.cpython-310.pyc', 'virtualenv/seed/wheels/__pycache__/bundle.cpython-310.pyc', 'virtualenv/seed/wheels/__pycache__/util.cpython-310.pyc', 'virtualenv/seed/wheels/__pycache__/periodic_update.cpython-310.pyc', 'virtualenv/seed/__pycache__/__init__.cpython-310.pyc', 'virtualenv/seed/__pycache__/seeder.cpython-310.pyc', 'virtualenv/__pycache__/report.cpython-310.pyc', 'virtualenv/__pycache__/__init__.cpython-310.pyc', 'virtualenv/__pycache__/version.cpython-310.pyc', 'virtualenv/__pycache__/info.cpython-310.pyc', 'virtualenv/create/debug.py', 'virtualenv/create/describe.py', 'virtualenv/create/pyenv_cfg.py', 'virtualenv/create/__init__.py', 'virtualenv/create/creator.py', 'virtualenv/create/__pycache__/pyenv_cfg.cpython-310.pyc', 'virtualenv/create/__pycache__/describe.cpython-310.pyc', 'virtualenv/create/__pycache__/__init__.cpython-310.pyc', 'virtualenv/create/__pycache__/creator.cpython-310.pyc', 'virtualenv/create/via_global_ref/venv.py', 'virtualenv/create/via_global_ref/store.py', 'virtualenv/create/via_global_ref/_virtualenv.py', 'virtualenv/create/via_global_ref/api.py', 'virtualenv/create/via_global_ref/__init__.py', 'virtualenv/create/via_global_ref/builtin/via_global_self_do.py', 'virtualenv/create/via_global_ref/builtin/ref.py', 'virtualenv/create/via_global_ref/builtin/builtin_way.py', 'virtualenv/create/via_global_ref/builtin/__init__.py', 'virtualenv/create/via_global_ref/builtin/pypy/pypy3.py', 'virtualenv/create/via_global_ref/builtin/pypy/__init__.py', 'virtualenv/create/via_global_ref/builtin/pypy/pypy2.py', 'virtualenv/create/via_global_ref/builtin/pypy/common.py', 'virtualenv/create/via_global_ref/builtin/pypy/__pycache__/__init__.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/pypy/__pycache__/common.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/pypy/__pycache__/pypy3.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/pypy/__pycache__/pypy2.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/__pycache__/ref.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/__pycache__/__init__.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/__pycache__/builtin_way.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/__pycache__/via_global_self_do.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/python2/python2.py', 'virtualenv/create/via_global_ref/builtin/python2/__init__.py', 'virtualenv/create/via_global_ref/builtin/python2/site.py', 'virtualenv/create/via_global_ref/builtin/python2/__pycache__/__init__.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/python2/__pycache__/python2.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/cpython/cpython3.py', 'virtualenv/create/via_global_ref/builtin/cpython/mac_os.py', 'virtualenv/create/via_global_ref/builtin/cpython/__init__.py', 'virtualenv/create/via_global_ref/builtin/cpython/cpython2.py', 'virtualenv/create/via_global_ref/builtin/cpython/common.py', 'virtualenv/create/via_global_ref/builtin/cpython/__pycache__/mac_os.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/cpython/__pycache__/__init__.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/cpython/__pycache__/common.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/cpython/__pycache__/cpython3.cpython-310.pyc', 'virtualenv/create/via_global_ref/builtin/cpython/__pycache__/cpython2.cpython-310.pyc', 'virtualenv/create/via_global_ref/__pycache__/__init__.cpython-310.pyc', 'virtualenv/create/via_global_ref/__pycache__/api.cpython-310.pyc', 'virtualenv/create/via_global_ref/__pycache__/venv.cpython-310.pyc', 'virtualenv/create/via_global_ref/__pycache__/store.cpython-310.pyc', 'virtualenv/config/env_var.py', 'virtualenv/config/__init__.py', 'virtualenv/config/ini.py', 'virtualenv/config/convert.py', 'virtualenv/config/cli/parser.py', 'virtualenv/config/cli/__init__.py', 'virtualenv/config/cli/__pycache__/__init__.cpython-310.pyc', 'virtualenv/config/cli/__pycache__/parser.cpython-310.pyc', 'virtualenv/config/__pycache__/ini.cpython-310.pyc', 'virtualenv/config/__pycache__/convert.cpython-310.pyc', 'virtualenv/config/__pycache__/__init__.cpython-310.pyc', 'virtualenv/config/__pycache__/env_var.cpython-310.pyc', 'virtualenv/util/zipapp.py', 'virtualenv/util/lock.py', 'virtualenv/util/error.py', 'virtualenv/util/__init__.py', 'virtualenv/util/six.py', 'virtualenv/util/subprocess/_win_subprocess.py', 'virtualenv/util/subprocess/__init__.py', 'virtualenv/util/subprocess/__pycache__/__init__.cpython-310.pyc', 'virtualenv/util/__pycache__/__init__.cpython-310.pyc', 'virtualenv/util/__pycache__/lock.cpython-310.pyc', 'virtualenv/util/__pycache__/error.cpython-310.pyc', 'virtualenv/util/__pycache__/zipapp.cpython-310.pyc', 'virtualenv/util/__pycache__/six.cpython-310.pyc', 'virtualenv/util/path/_win.py', 'virtualenv/util/path/_sync.py', 'virtualenv/util/path/__init__.py', 'virtualenv/util/path/_permission.py', 'virtualenv/util/path/__pycache__/__init__.cpython-310.pyc', 'virtualenv/util/path/__pycache__/_permission.cpython-310.pyc', 'virtualenv/util/path/__pycache__/_win.cpython-310.pyc', 'virtualenv/util/path/__pycache__/_sync.cpython-310.pyc', 'virtualenv/util/path/_pathlib/via_os_path.py', 'virtualenv/util/path/_pathlib/__init__.py', 'virtualenv/util/path/_pathlib/__pycache__/__init__.cpython-310.pyc', 'virtualenv/run/session.py', 'virtualenv/run/__init__.py', 'virtualenv/run/plugin/discovery.py', 'virtualenv/run/plugin/seeders.py', 'virtualenv/run/plugin/activators.py', 'virtualenv/run/plugin/__init__.py', 'virtualenv/run/plugin/base.py', 'virtualenv/run/plugin/creators.py', 'virtualenv/run/plugin/__pycache__/__init__.cpython-310.pyc', 'virtualenv/run/plugin/__pycache__/activators.cpython-310.pyc', 'virtualenv/run/plugin/__pycache__/seeders.cpython-310.pyc', 'virtualenv/run/plugin/__pycache__/base.cpython-310.pyc', 'virtualenv/run/plugin/__pycache__/discovery.cpython-310.pyc', 'virtualenv/run/plugin/__pycache__/creators.cpython-310.pyc', 'virtualenv/run/__pycache__/__init__.cpython-310.pyc', 'virtualenv/run/__pycache__/session.cpython-310.pyc']
        },
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        python_requires = '>=3.6',
        obsoletes = [],
    )
