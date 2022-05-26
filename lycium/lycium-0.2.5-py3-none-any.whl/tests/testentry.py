#!/usr/bin/env python
# -*- coding: utf-8 -*-

import asyncio

if __name__ == '__main__':
    # from .dbunittest import test_dbunit_rdbms_tests, test_dbunit_mongodb_tests, test_dbunittest_main, test_rdbms_stored_procedure
    from .testhttpclient import test_http_query, test_http_with_simple_proxy, test_parse_http_proxies
    # asyncio.run(test_rdbms_stored_procedure())
    # asyncio.run(test_dbunit_rdbms_tests())
    # asyncio.run(test_dbunit_mongodb_tests())
    # test_dbunittest_main()
    # from .local_mongotest import test_mongodb_api
    # test_mongodb_api()
    test_parse_http_proxies()
    test_http_with_simple_proxy()
    