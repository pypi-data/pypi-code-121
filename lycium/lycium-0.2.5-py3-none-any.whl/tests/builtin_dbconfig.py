
rdbms = {
    'debug_sqlite': {
        'connector': 'sqlite',
        'host': './debug.sqlite.db',
        'db': 'main'
    },
    'ignore_debug_mssql': {
        'connector': "mssql",
        'driver': "",
        'host': "127.0.0.1",
        'port': 1433,
        'user': "changeit",
        'pwd': "changeit",
        'db': "changeit"
    },
    'ignore_debug_oracle': {
        'connector': "oracle",
        'driver': "",
        'host': "127.0.0.1",
        'port': 1433,
        'user': "changeit",
        'pwd': "changeit",
        'db': "changeit"
    },
    'ignore_debug_pg': {
        'connector': "postgresql",
        'driver': "",
        'host': "127.0.0.1",
        'port': 5432,
        'user': "changeit",
        'pwd': "changeit",
        'db': "changeit",
        # 'ext_args': {'sslmode': 'require'}
    },
    'debug_mssql': {
        'connector': "mssql",
        'driver': "",
        'host': "127.0.0.1",
        'port': 1433,
        'user': "changeit",
        'pwd': "changeit",
        'db': "changeit"
    },
    'debug_oracle': {
        'connector': "oracle",
        'driver': "",
        'host': "127.0.0.1",
        'port': 1521,
        'user': "changeit",
        'pwd': "changeit",
        'db': "helowin"
    },
    'debug_cockroach': {
        'connector': "cockroachdb",
        'host': "127.0.0.1",
        'port': 26257,
        'user': "root",
        'pwd': "",
        'db': "changeit",
        # 'ext_args': {'sslmode': 'require'}
    },
}

mongodbs = {
    'debug_mongo': {
        'connector': 'mongodb',
        'host':  '127.0.0.1',
        'port': 27017,
        'user': 'changeit',
        'pwd': 'changeit',
        'db': 'changeit'
    }
}
