#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.asynchttphandler import async_route, args_as_dict, request_body_as_json
from lycium.dbproxy import DbProxy
from lycium.webapplication import WebApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

rdbms = {
    'ignore_debug_mssql': {
        'connector': "mssql",
        'driver': "pymssql",
        'host': "127.0.0.1",
        'port': 1433,
        'user': "sa",
        'pwd': "changeit",
        'db': "changeit"
    },
    'debug_cockroach': {
        'connector': 'cockroachdb',
        'host': '10.246.247.210',
        'port': 26257,
        'user': 'medical_community_dev',
        'pwd': 'HgCSVGgAwCfBTJF7',
        'db': 'medical_community_dev',
        # 'ext_args': {
        #     'sslmode': 'require'
        # }
    },
    'debug_sqlite': {
        'connector': 'sqlite',
        'host': './debug.sqlite.db',
        'db': 'main'
    }
}

@async_route('/healthz', methods=['GET'])
@tornado.gen.coroutine
def test_healthz(handler, request):
    return 'hello'

@async_route('/debug', methods=['GET'])
@tornado.gen.coroutine
def test_query_sql(handler, request):
    sql1 = 'SELECT * FROM ods_xhhk_ehr_health_record LIMIT 2000'
    sql2 = 'SELECT * FROM ods_xhhk_lis_report_info LIMIT 2000'
    # sql3 = 'SELECT * FROM ods_xhhk_lis_report_info LIMIT 2000'
    t1 = time.time()
    print(' << access on %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))))
    result = yield [
        DbProxy().exec_query('debug_cockroach', sql1),
        DbProxy().exec_query('debug_cockroach', sql2),
        DbProxy().exec_query('debug_cockroach', sql1),
    ]
    t2 = time.time()
    print(" -- records:%d dt %.2f" % (len(result), t2 - t1))
    return 'done'

def test_db_api():
    DbProxy().setup_rdbms(rdbms)

    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    print('starting...')
    IOLoop.instance().start()

if __name__ == "__main__":
    test_db_api()
