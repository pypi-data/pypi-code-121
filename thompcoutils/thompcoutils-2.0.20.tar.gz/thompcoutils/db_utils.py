from thompcoutils.log_utils import get_logger
from thompcoutils.config_utils import ConfigManager
from thompcoutils.test_utils import assert_test
import logging
import sqlobject
import os


class DBConfig:
    def __init__(self, cfg_mgr, section=None):
        if section is None:
            section = 'DB CONNECTION'
        logger = get_logger()
        logger.debug('Initialing DbConfig')
        self.ssh_tunnel = None
        self.type = cfg_mgr.read_entry(section, "type", default_value="mysql")
        self.sqlite_file = cfg_mgr.read_entry(section, "sqlite file", default_value="licenseserver.sqlite")
        self.db_host = cfg_mgr.read_entry(section, "db_host", default_value="localhost")
        self.db_username = cfg_mgr.read_entry(section, "db_username", default_value="my db user name")
        self.db_password = cfg_mgr.read_entry(section, "db_password", default_value="my db user password")
        self.schema = cfg_mgr.read_entry(section, "schema", default_value="my db schema")
        self.db_port = cfg_mgr.read_entry(section, "db_port", default_value=3306)
        self.rebuild = cfg_mgr.read_entry(section, "rebuild", default_value=False)
        self.ssh_username = cfg_mgr.read_entry(section, "ssh_username", default_value="")
        self.ssh_password = cfg_mgr.read_entry(section, "ssh_password", default_value="")
        self.ssh_host = cfg_mgr.read_entry(section, "ssh_host", default_value="localhost")
        self.use_ssh = cfg_mgr.read_entry(section, "use_ssh", default_value=False)
        self.ssh_timeout = cfg_mgr.read_entry(section, "ssh_timeout", default_value=5.0)
        self.ssh_tunnel_timeout = cfg_mgr.read_entry(section, "ssh_tunnel_timeout", default_value=5.0)
        if self.ssh_username == '':
            self.ssh_username = None
        if self.ssh_password == '':
            self.ssh_password = None


class DbUtils:
    def __init__(self, cfg_mgr=None, db_type=None, db_host=None, db_username=None, db_password=None, schema=None,
                 db_port=None, sqlite_file=None, ssh_username=None, ssh_password=None,
                 use_ssh=False, ssh_host=None, ssh_timeout=None, ssh_tunnel_timeout=None, section=None):
        logger = get_logger()
        self.connection = None
        self.ssh_tunnel = None
        self.tables = []
        self.db_type = db_type
        self.sqlite_file = sqlite_file
        self.db_host = db_host
        self.db_username = db_username
        self.db_password = db_password
        self.schema = schema
        self.db_port = db_port
        self.use_ssh = use_ssh
        self.ssh_host = ssh_host
        self.ssh_username = ssh_username
        self.ssh_password = ssh_password
        self.ssh_timeout = ssh_timeout
        self.ssh_tunnel_timeout = ssh_tunnel_timeout

        if cfg_mgr is not None:
            db_cfg = DBConfig(cfg_mgr=cfg_mgr, section=section)
            self.db_type = db_cfg.type
            self.sqlite_file = db_cfg.sqlite_file
            self.db_host = db_cfg.db_host
            self.db_username = db_cfg.db_username
            self.db_password = db_cfg.db_password
            self.schema = db_cfg.schema
            self.db_port = db_cfg.db_port
            self.use_ssh = db_cfg.use_ssh
            self.ssh_username = db_cfg.ssh_username
            self.ssh_password = db_cfg.ssh_password
            self.ssh_timeout = db_cfg.ssh_timeout
            self.ssh_tunnel_timeout = db_cfg.ssh_tunnel_timeout
        if self.db_type == "sqlite":
            if self.sqlite_file is None:
                raise RuntimeError('"sqlite" requires "sqlite_file"')
            else:
                logger.debug("Using {} Sqlite database".format(self.sqlite_file))
                self._connect_sqlite(self.sqlite_file)
        elif self.db_type == "postgres":
            logger.debug('Using postgress database {} at {}'.format(self.schema, self.db_host))
            self._connect_postgres()
        elif "mysql" in self.db_type:
            logger.debug('Using mysql database {} at {}'.format(self.schema, self.db_host))
            self._connect_mysql()
        elif self.db_type == "odbc":
            raise RuntimeError("ODBC not implemented yet")
        else:
            raise RuntimeError("No database type selected")
        try:
            self.create_table(_TestTable)
            self.drop_tables([_TestTable])
        except Exception as e:
            logger.exception('Could not connect to database:{}'.format(e))

    def _connect_uri(self, uri):
        self.connection = sqlobject.sqlhub.processConnection = sqlobject.connectionForURI(uri)

    def _connect_sqlite(self, file_path):
        uri = "sqlite:" + file_path
        self._connect_uri(uri)

    def _connect_postgres(self):
        port_str = ""
        if self.db_port is not None:
            port_str = ":" + str(self.db_port)
        uri = "postgres://" + self.db_username + ":" + self.db_password + "@" + self.db_host + port_str + "/" + \
              self.schema
        self._connect_uri(uri)

    def _connect_mysql(self):
        import sshtunnel
        import mysql.connector
        logger = get_logger()
        if self.use_ssh:
            sshtunnel.SSH_TIMEOUT = self.ssh_timeout
            sshtunnel.TUNNEL_TIMEOUT = self.ssh_tunnel_timeout
            try:
                self.ssh_tunnel = sshtunnel.SSHTunnelForwarder(self.db_host,
                                                               ssh_username=self.ssh_username,
                                                               ssh_password=self.ssh_password,
                                                               remote_bind_address=(self.db_host, self.db_port))
                self.ssh_tunnel.daemon_forward_servers = True
                self.ssh_tunnel.start()
                self.connection = mysql.connector.connect(user=self.db_username, password=self.db_password,
                                                          host=self.ssh_host, port=self.ssh_tunnel.local_bind_port,
                                                          database=self.schema)
            except sshtunnel.BaseSSHTunnelForwarderError as e:
                logger.exception('Could not create an SSH Tunnel: {}'.format(str(e.value)))
                raise Exception(e)
            except mysql.connector.InterfaceError as e:
                logger.exception('Could not connect: {}'.format(e.msg))
                raise Exception(e)

        port_str = ""
        if self.db_port is not None:
            port_str = ":" + str(self.db_port)
        uri = "mysql://" + self.db_username + ":" + self.db_password + "@" + self.db_host + port_str + "/" + \
              self.schema
        self._connect_uri(uri)

    def add_table(self, table):
        self.tables.append(table)

    def set_tables(self, tables):
        self.tables = tables

    def shutdown(self):
        if self.ssh_tunnel is not None:
            self.ssh_tunnel.stop_flashing()

    def table_exists(self, table_name):
        return self.connection.tableExists(table_name.sqlmeta.table)

    def create_table(self, table):
        logger = get_logger()
        if not self.table_exists(table):
            logger.debug("creating table {}.{}".format(self.schema, str(table.sqlmeta.table)))
            table.createTable()
            logger.debug("created table {}.{}".format(self.schema, str(table.sqlmeta.table)))

    def create_tables(self, tables=None):
        logger = get_logger()
        logger.debug("Creating tables...")
        if tables is None:
            tables = self.tables
        for table in tables:
            self.create_table(table)

    def drop_tables(self, tables=None):
        logger = get_logger()
        logger.debug("Dropping tables...")
        if tables is None:
            tables = self.tables
        for table in tables:
            logger.debug("dropping table {}.{}".format(self.schema, str(table.sqlmeta.table)))
            table.dropTable(cascade=True, ifExists=True)
            logger.debug("dropped table {}".format(str(table.sqlmeta.table)))


class _TestTable(sqlobject.SQLObject):
    # noinspection PyPep8Naming,PyClassHasNoInit
    class sqlmeta:
        table = "Test_table"
    first_name = sqlobject.StringCol()
    last_name = sqlobject.StringCol()
    age = sqlobject.IntCol
    salary = sqlobject.FloatCol()

    @staticmethod
    def validate():
        _TestTable(first_name='Jordan', last_name='Thompson', age=35, salary=20.5)
        query = _TestTable.select(_TestTable.q.first_name == 'Jordan')
        assert_test(query.count() == 1, message='Ensuring count is 1', error='Count is not 1', passed='Count is 1')
        assert_test(query.getOne().last_name == 'Thompson', message='Ensuring data is inserted',
                    passed='Data inserted correctly')


class _TestDatabase(DbUtils):
    def __init__(self, db_cfg_file):
        super().__init__(db_cfg_file)
        self.set_tables([_TestTable])


def _main():
    config_file_name = "testing DbConfig only.ini"
    if not os.path.exists(config_file_name):
        cfg_mgr = ConfigManager(config_file_name, create=True)
        cfg_mgr.write(out_file=config_file_name)
        print('This should not print out!')
    test_db = _TestDatabase(db_cfg_file=config_file_name)
    if test_db.table_exists(_TestTable):
        test_db.drop_tables()
    assert_test(not test_db.table_exists(_TestTable),
                message='Testing that table {}.{} was successfully removed'.format(test_db.schema,
                                                                                   _TestTable.sqlmeta.table),
                error='Table {}.{} should not exist'.format(test_db.schema, _TestTable.sqlmeta.table),
                passed='Table {}.{} removed successfully'.format(test_db.schema, _TestTable.sqlmeta.table))
    test_db.create_tables()
    assert_test(test_db.table_exists(_TestTable),
                message='Testing that table {}.{} was successfully created'.format(test_db.schema,
                                                                                   _TestTable.sqlmeta.table),
                error='Table {}.{} should exist'.format(test_db.schema, _TestTable.sqlmeta.table),
                passed='Table {}.{} created successfully'.format(test_db.schema, _TestTable.sqlmeta.table))
    _TestTable.validate()
    test_db.shutdown()


if __name__ == "__main__":
    logging.basicConfig()
    logging.root.setLevel(logging.DEBUG)
    logging.getLogger('paramiko.transport').setLevel(logging.WARN)
    logging.root.propagate = True
    _main()
