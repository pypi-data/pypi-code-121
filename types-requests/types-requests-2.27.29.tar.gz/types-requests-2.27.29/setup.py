from setuptools import setup

name = "types-requests"
description = "Typing stubs for requests"
long_description = '''
## Typing stubs for requests

This is a PEP 561 type stub package for the `requests` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `requests`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/requests. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `466f9c2ad7bb65702b268081bcc753778f43f6a0`.
'''.lstrip()

setup(name=name,
      version="2.27.29",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/requests.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=['types-urllib3<1.27'],
      packages=['requests-stubs'],
      package_data={'requests-stubs': ['__init__.pyi', 'adapters.pyi', 'api.pyi', 'auth.pyi', 'compat.pyi', 'cookies.pyi', 'exceptions.pyi', 'hooks.pyi', 'models.pyi', 'packages/__init__.pyi', 'sessions.pyi', 'status_codes.pyi', 'structures.pyi', 'utils.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
