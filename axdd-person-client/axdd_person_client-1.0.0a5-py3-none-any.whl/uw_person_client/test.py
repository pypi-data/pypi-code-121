# Copyright 2022 UW-IT, University of Washington
# SPDX-License-Identifier: Apache-2.0

# This is just a test runner for coverage
from commonconf.backends import use_configuration_backend

if __name__ == '__main__':

    # setup app settings
    use_configuration_backend('conf.settings.AppSettings')

    from nose2 import discover
    discover()
