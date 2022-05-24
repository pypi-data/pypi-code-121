from setuptools import setup

name = "types-mypy-extensions"
description = "Typing stubs for mypy-extensions"
long_description = '''
## Typing stubs for mypy-extensions

This is a PEP 561 type stub package for the `mypy-extensions` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `mypy-extensions`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/mypy-extensions. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `54e11a1ec48ccfde21642fafe1e531117c0da9f6`.
'''.lstrip()

setup(name=name,
      version="0.4.18",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/mypy-extensions.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['mypy_extensions-stubs'],
      package_data={'mypy_extensions-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
