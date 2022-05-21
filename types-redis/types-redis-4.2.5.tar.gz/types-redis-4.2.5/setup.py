from setuptools import setup

name = "types-redis"
description = "Typing stubs for redis"
long_description = '''
## Typing stubs for redis

This is a PEP 561 type stub package for the `redis` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `redis`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/redis. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `8b58371278078d50c85128d74b1fc10c24029d21`.
'''.lstrip()

setup(name=name,
      version="4.2.5",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/redis.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['redis-stubs'],
      package_data={'redis-stubs': ['__init__.pyi', 'asyncio/__init__.pyi', 'asyncio/client.pyi', 'asyncio/connection.pyi', 'asyncio/lock.pyi', 'asyncio/retry.pyi', 'asyncio/sentinel.pyi', 'asyncio/utils.pyi', 'backoff.pyi', 'client.pyi', 'cluster.pyi', 'commands/__init__.pyi', 'commands/bf/__init__.pyi', 'commands/bf/commands.pyi', 'commands/bf/info.pyi', 'commands/cluster.pyi', 'commands/core.pyi', 'commands/graph/__init__.pyi', 'commands/graph/commands.pyi', 'commands/graph/edge.pyi', 'commands/graph/exceptions.pyi', 'commands/graph/node.pyi', 'commands/graph/path.pyi', 'commands/graph/query_result.pyi', 'commands/helpers.pyi', 'commands/json/__init__.pyi', 'commands/json/commands.pyi', 'commands/json/decoders.pyi', 'commands/json/path.pyi', 'commands/parser.pyi', 'commands/redismodules.pyi', 'commands/search/__init__.pyi', 'commands/search/aggregation.pyi', 'commands/search/commands.pyi', 'commands/search/query.pyi', 'commands/search/result.pyi', 'commands/sentinel.pyi', 'commands/timeseries/__init__.pyi', 'commands/timeseries/commands.pyi', 'commands/timeseries/info.pyi', 'commands/timeseries/utils.pyi', 'connection.pyi', 'crc.pyi', 'exceptions.pyi', 'lock.pyi', 'ocsp.pyi', 'retry.pyi', 'sentinel.pyi', 'typing.pyi', 'utils.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
