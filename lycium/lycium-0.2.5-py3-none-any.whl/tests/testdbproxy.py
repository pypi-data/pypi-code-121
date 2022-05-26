from lycium.dbproxy import DbProxy


if __name__ == '__main__':
    test_config = {
        'connector': 'cockroachdb',
        'host': '10.246.247.210',
        'port': 26257,
        'user': 'bennx',
        'pwd': 'appAZvxj$tcnU2rN',
        'db': 'bennx'}
    test_dbproxy = DbProxy()
    assert test_dbproxy.setup_rdbms_connection('test', test_config)