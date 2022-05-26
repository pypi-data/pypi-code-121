
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
        'host': "10.246.240.110",
        'port': 1433,
        'user': "xhhk",
        'pwd': "SAq1w2e3r4",
        'db': "xhhk"
    },
    'debug_oracle': {
        'connector': "oracle",
        'driver': "",
        'host': "10.246.240.110",
        'port': 1521,
        'user': "xhhk",
        'pwd': "q1w2e3r4",
        'db': "helowin"
    },
    'debug_cockroach': {
        'connector': "cockroachdb",
        'host': "127.0.0.1",
        'port': 26257,
        'user': "root",
        'pwd': "",
        'db': "local_demo",
        # 'ext_args': {'sslmode': 'require'}
    },
}

mongodbs = {
    # 'debug_mongo': {
    #     'connector': 'mongodb',
    #     'host':  '10.246.247.204',
    #     'port': 27016,
    #     'user': 'xhhkmedical',
    #     'pwd': 'ADu45ExwH1WQ15ee',
    #     'db': 'xhhkmedical'
    # },
    'debug_mongo': {
        'connector': 'mongodb',
        'host':  '10.246.247.204',
        'port': 27016,
        'user': 'dev_xhhkmedical',
        'pwd': 'h4wgrd1Q9rCaaVu0',
        'db': 'dev_xhhkmedical'
    }
}
