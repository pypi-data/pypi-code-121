# -*- coding: utf-8 -*-
# Copyright © 2022 Contrast Security, Inc.
# See https://www.contrastsecurity.com/enduser-terms-0317a for more details.
"""
Contains dependencies of the agent that we have chosen to vendor

Vendoring dependencies can make life easier on both ourselves and our
customers. Some customers have fairly constrained environments which can make
it difficult for them to install our dependencies. By vendoring, we reduce the
burden for them. Vendoring also allows ourselves to use specific, known stable
versions of dependencies without worrying about conflicts in customer
environments. This can be especially useful for common packages that are
expected to already exist in most environments (e.g. `ruamel.yaml`).

The code under this directory should be ignored when linting and when
calculating test coverage since it is technically out of our control. In
general we should not make changes to the code in this directory other than to
introduce a different version of a particular package.

A list of included packages can be found under extern-requirements.txt.
"""
