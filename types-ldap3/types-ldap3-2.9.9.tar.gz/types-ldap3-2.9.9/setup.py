from setuptools import setup

name = "types-ldap3"
description = "Typing stubs for ldap3"
long_description = '''
## Typing stubs for ldap3

This is a PEP 561 type stub package for the `ldap3` package.
It can be used by type-checking tools like mypy, PyCharm, pytype etc. to check code
that uses `ldap3`. The source for this package can be found at
https://github.com/python/typeshed/tree/master/stubs/ldap3. All fixes for
types and metadata should be contributed there.

See https://github.com/python/typeshed/blob/master/README.md for more details.
This package was generated from typeshed commit `466f9c2ad7bb65702b268081bcc753778f43f6a0`.
'''.lstrip()

setup(name=name,
      version="2.9.9",
      description=description,
      long_description=long_description,
      long_description_content_type="text/markdown",
      url="https://github.com/python/typeshed",
      project_urls={
          "GitHub": "https://github.com/python/typeshed",
          "Changes": "https://github.com/typeshed-internal/stub_uploader/blob/main/data/changelogs/ldap3.md",
          "Issue tracker": "https://github.com/python/typeshed/issues",
          "Chat": "https://gitter.im/python/typing",
      },
      install_requires=[],
      packages=['ldap3-stubs'],
      package_data={'ldap3-stubs': ['__init__.pyi', 'abstract/__init__.pyi', 'abstract/attrDef.pyi', 'abstract/attribute.pyi', 'abstract/cursor.pyi', 'abstract/entry.pyi', 'abstract/objectDef.pyi', 'core/__init__.pyi', 'core/connection.pyi', 'core/exceptions.pyi', 'core/pooling.pyi', 'core/rdns.pyi', 'core/results.pyi', 'core/server.pyi', 'core/timezone.pyi', 'core/tls.pyi', 'core/usage.pyi', 'extend/__init__.pyi', 'extend/microsoft/__init__.pyi', 'extend/microsoft/addMembersToGroups.pyi', 'extend/microsoft/dirSync.pyi', 'extend/microsoft/modifyPassword.pyi', 'extend/microsoft/persistentSearch.pyi', 'extend/microsoft/removeMembersFromGroups.pyi', 'extend/microsoft/unlockAccount.pyi', 'extend/novell/__init__.pyi', 'extend/novell/addMembersToGroups.pyi', 'extend/novell/checkGroupsMemberships.pyi', 'extend/novell/endTransaction.pyi', 'extend/novell/getBindDn.pyi', 'extend/novell/listReplicas.pyi', 'extend/novell/nmasGetUniversalPassword.pyi', 'extend/novell/nmasSetUniversalPassword.pyi', 'extend/novell/partition_entry_count.pyi', 'extend/novell/removeMembersFromGroups.pyi', 'extend/novell/replicaInfo.pyi', 'extend/novell/startTransaction.pyi', 'extend/operation.pyi', 'extend/standard/PagedSearch.pyi', 'extend/standard/PersistentSearch.pyi', 'extend/standard/__init__.pyi', 'extend/standard/modifyPassword.pyi', 'extend/standard/whoAmI.pyi', 'operation/__init__.pyi', 'operation/abandon.pyi', 'operation/add.pyi', 'operation/bind.pyi', 'operation/compare.pyi', 'operation/delete.pyi', 'operation/extended.pyi', 'operation/modify.pyi', 'operation/modifyDn.pyi', 'operation/search.pyi', 'operation/unbind.pyi', 'protocol/__init__.pyi', 'protocol/controls.pyi', 'protocol/convert.pyi', 'protocol/formatters/__init__.pyi', 'protocol/formatters/formatters.pyi', 'protocol/formatters/standard.pyi', 'protocol/formatters/validators.pyi', 'protocol/microsoft.pyi', 'protocol/novell.pyi', 'protocol/oid.pyi', 'protocol/persistentSearch.pyi', 'protocol/rfc2696.pyi', 'protocol/rfc2849.pyi', 'protocol/rfc3062.pyi', 'protocol/rfc4511.pyi', 'protocol/rfc4512.pyi', 'protocol/rfc4527.pyi', 'protocol/sasl/__init__.pyi', 'protocol/sasl/digestMd5.pyi', 'protocol/sasl/external.pyi', 'protocol/sasl/kerberos.pyi', 'protocol/sasl/plain.pyi', 'protocol/sasl/sasl.pyi', 'protocol/schemas/__init__.pyi', 'protocol/schemas/ad2012R2.pyi', 'protocol/schemas/ds389.pyi', 'protocol/schemas/edir888.pyi', 'protocol/schemas/edir914.pyi', 'protocol/schemas/slapd24.pyi', 'strategy/__init__.pyi', 'strategy/asyncStream.pyi', 'strategy/asynchronous.pyi', 'strategy/base.pyi', 'strategy/ldifProducer.pyi', 'strategy/mockAsync.pyi', 'strategy/mockBase.pyi', 'strategy/mockSync.pyi', 'strategy/restartable.pyi', 'strategy/reusable.pyi', 'strategy/safeRestartable.pyi', 'strategy/safeSync.pyi', 'strategy/sync.pyi', 'utils/__init__.pyi', 'utils/asn1.pyi', 'utils/ciDict.pyi', 'utils/config.pyi', 'utils/conv.pyi', 'utils/dn.pyi', 'utils/hashed.pyi', 'utils/log.pyi', 'utils/ntlm.pyi', 'utils/port_validators.pyi', 'utils/repr.pyi', 'utils/tls_backport.pyi', 'utils/uri.pyi', 'version.pyi', 'METADATA.toml']},
      license="Apache-2.0 license",
      classifiers=[
          "License :: OSI Approved :: Apache Software License",
          "Programming Language :: Python :: 3",
          "Typing :: Stubs Only",
      ]
)
