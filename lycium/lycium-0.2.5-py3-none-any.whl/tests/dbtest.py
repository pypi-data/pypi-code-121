#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.asynchttphandler import async_route, args_as_dict, request_body_as_json
from lycium.dbproxy import DbProxy
from lycium.webapplication import WebApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

rdbms = {
    'debug_mssql': {
        'connector': "mssql",
        'driver': "pymssql",
        'host': "10.10.61.22",
        'port': 1433,
        'user': "sa",
        'pwd': "server@1",
        'db': "rris"
    }
}

@async_route('/debug', methods=['GET'])
@tornado.gen.coroutine
def test_query_sql(handler, request):
    sql = 'SELECT * FROM RRIS.dbo.SmartPrint_GetReportData where 1=0'
    result = yield DbProxy().exec_query('debug_mssql', sql)
    print(result)
    return 'abc'

def main():
    DbProxy().setup_rdbms(rdbms)

    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    print('starting...')
    IOLoop.instance().start()

if __name__ == "__main__":
    main()
