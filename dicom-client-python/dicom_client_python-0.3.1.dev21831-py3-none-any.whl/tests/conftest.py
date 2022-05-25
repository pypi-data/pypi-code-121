# Copyright (c) Microsoft Corporation.
# Licensed under the MIT license.

from os import environ


def pytest_addoption(parser):
    parser.addoption("--auth_connection_info", default=environ.get("AUTH_CONNECTION_INFO"))
