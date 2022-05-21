from setuptools import setup

name = "types-filelock"
description = "Typing stubs for filelock"
long_description = '''
## Typing stubs for filelock

This is a PEP 561 type stub package for the `filelock` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `filelock`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/filelock. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8b58371278078d50c85128d74b1fc10c24029d21`.
'''.lstrip()

setup(name=name,
      version="3.2.6",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/filelock.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['filelock-stubs'],
      package_data={'filelock-stubs': ['__init__.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
