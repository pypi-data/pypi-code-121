
# This is a list of always applied configurations. They do not depend on the application.

starting_config = [

    # MinIO configs
    ("spark.hadoop.fs.s3a.path.style.access", True),
    ("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem"),

    # Hive configs
    ('hive.server2.enable.doAs', True),
    ('hive.metastore.client.connect.retry.delay', 5),
    ('hive.metastore.client.socket.timeout', 1800),
    ('spark.hadoop.dfs.client.use.datanode.hostname', True),
    ('spark.sql.warehouse.dir', '/warehouse/tablespace/managed/hive'),
    ("spark.sql.catalogImplementation", "hive"),

]