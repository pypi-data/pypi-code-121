from string import Template
import os
from time import sleep
from typing import Union, Optional, Tuple, Any, List, Dict

from deprecation import deprecated

from divinegift.errors import MethodNotAllowedError

try:
    from sqlalchemy import create_engine, MetaData, Table, text
    from sqlalchemy.engine import Engine
    from sqlalchemy.exc import DatabaseError
    from sqlalchemy.engine.base import Connection as SQLAlchemyConnection
except ImportError:
    raise ImportError("sqlalchemy isn't installed. Run: pip install -U sqlalchemy")

from divinegift import version


class DBClient:
    def __init__(self, db_conn: dict, future=True, do_initialize=True, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs
        self.db_conn = db_conn
        self.future = future

        self.engine: Optional[Engine] = None
        self.conn: Optional[SQLAlchemyConnection] = None
        self.metadata: Optional[MetaData] = None

        if do_initialize:
            self.create_engine()

    def get_conn_str(self) -> str:
        if self.db_conn.get('dialect') == 'mssql+pytds':
            from sqlalchemy.dialects import registry
            registry.register("mssql.pytds", "sqlalchemy_pytds.dialect", "MSDialect_pytds")
        if self.db_conn.get('db_host') and self.db_conn.get('db_port'):
            if 'oracle' in self.db_conn.get('dialect').lower() and '.orcl' in self.db_conn.get('db_name'):
                connect_str = '{dialect}://{db_user}:{db_pass}@{db_host}:{db_port}/?service_name={db_name}'.format(
                    **self.db_conn)
            else:
                connect_str = '{dialect}://{db_user}:{db_pass}@{db_host}:{db_port}/{db_name}'.format(**self.db_conn)
        else:
            connect_str = '{dialect}://{db_user}:{db_pass}@{db_name}'.format(**self.db_conn)

        return connect_str

    def create_engine(self) -> None:
        connect_str = self.get_conn_str()
        self.engine = create_engine(connect_str, future=self.future, *self.args, **self.kwargs)

    def create_conn(self) -> None:
        if not self.conn:
            self.conn = self.engine.connect()

    def create_raw_conn(self) -> None:
        if not self.conn:
            self.conn = self.engine.raw_connection()

    def create_metadata(self) -> None:
        if not self.metadata:
            self.create_conn()
            self.metadata = MetaData(bind=self.engine)

    def set_args(self, *args, **kwargs):
        self.args = args
        self.kwargs = kwargs

    def set_conn(self) -> None:
        """
        Create connection for SQLAlchemy
        :return: Engine, Connection, Metadata
        """
        self.create_engine()
        self.create_conn()
        self.create_metadata()

    def set_raw_conn(self) -> None:
        """
        Create raw connection for SQLAlchemy
        :return: Connection
        """
        connect_str = self.get_conn_str()

        self.engine = create_engine(connect_str, *self.args, **self.kwargs)
        self.conn = self.engine.raw_connection()
        self.metadata = MetaData(bind=self.conn)

    def get_conn(self, fields: Union[str, list] = 'conn') -> Tuple[Optional[Any], ...]:
        """
        Return connection fields: engine, conn, metadata
        :param fields: str or list of str
        :return: tuple or single value
        """
        if isinstance(fields, str):
            return self.__dict__.get(fields)
        elif isinstance(fields, list):
            return tuple([self.__dict__.get(x) for x in fields])
        else:
            raise MethodNotAllowedError('This type of fields is not allowed')

    def close_conn(self):
        self.conn.close()
        self.engine.dispose()
        self.conn = None

    def check_connection_status(self):
        if 'oracle' in self.db_conn.get('dialect').lower():
            d = self.get_data_row('select dummy from dual')
        else:
            d = self.get_data_row("select 'x' as dummy")
        if (v := d.get('dummy')) is None or v != 'x':
            self.close_conn()
            self.set_conn()

    @staticmethod
    def get_sql(filename: str, encoding: str = 'utf-8') -> str:
        """
        Get sql string from file
        :param filename: File name
        :param encoding: Encoding of file
        :return: String with sql
        """
        with open(filename, 'r', encoding=encoding) as file:
            sql = file.read()
        return sql

    def get_data(self, sql: str, encoding: str = 'utf-8', print_script=False, max_attempts=5, **kwargs) -> List[Dict]:
        """
        Get raw data from sql data as dict
        :param sql: File with sql which need to execute or script itself
        :param encoding: Encoding of file
        :param print_script: Print script text to console
        :param max_attempts: Max count  of tries to run script
        :param kwargs: List with additional data
        :return: Dictionary
        """
        if not self.conn:
            self.create_conn()

        if os.path.exists(sql):
            script_t = Template(self.get_sql(sql, encoding))
        else:
            script_t = Template(sql)
        script = script_t.safe_substitute(**kwargs)

        if print_script:
            print(script)

        res = self._execute(script, max_attempts)
        ress = [dict(row) for row in res]

        return ress

    def get_data_row(self, sql: str, index: int = 0, encoding: str = 'utf-8',
                     print_script=False, max_attempts=5, **kwargs) -> Optional[Dict]:
        """
        Get raw data from sql data as dict
        :param sql: File with sql which need to execute or script itself
        :param index: index of returning row
        :param encoding: Encoding of file
        :param print_script: Print script text to console
        :param max_attempts: Max count  of tries to run script
        :param kwargs: List with additional data
        :return: Dictionary
        """
        if not self.conn:
            self.create_conn()

        if os.path.exists(sql):
            script_t = Template(self.get_sql(sql, encoding))
        else:
            script_t = Template(sql)
        script = script_t.safe_substitute(**kwargs)

        if print_script:
            print(script)

        res = self._execute(script, max_attempts)
        ress = [dict(row) for row in res]

        try:
            ress = ress[index]
        except:
            ress = None

        return ress

    def _execute(self, script, max_attempts):
        res = []
        trns = None
        for _ in range(max_attempts):
            try:
                if not self.future:
                    trns = self.conn.begin()
                res = self.conn.execute(text(script))
                self.commit(trns)
                break
            except DatabaseError:
                self.rollback(trns)
                try:
                    self.close_conn()
                except:
                    pass
                sleep(10)
                self.set_conn()
        return res

    def run_script(self, sql: str, encoding: str = 'utf-8', print_script=False, max_attempts=5, **kwargs) -> None:
        """
        Run custom script
        :param sql: File with sql which need to execute
        :param encoding: Encoding of file
        :param print_script: Print script text to console
        :param max_attempts: Max count  of tries to run script
        :param kwargs: List with additional data
        :return: None
        """
        if not self.conn:
            self.create_conn()

        if os.path.exists(sql):
            script_t = Template(self.get_sql(sql, encoding))
        else:
            script_t = Template(sql)
        script = script_t.safe_substitute(**kwargs)

        if print_script:
            print(script)

        self._execute(script, max_attempts)

    def commit(self, transaction=None):
        if transaction:
            transaction.commit()
        else:
            self.conn.commit()

    def rollback(self, transaction=None):
        if transaction:
            transaction.rollback()
        else:
            self.conn.rollback()

    def begin_transaction(self):
        return self.engine.begin()


@deprecated(deprecated_in='1.3.9', current_version=version, details='Use class Connection instead')
def get_conn(db_conn: dict):
    conn_obj = DBClient(db_conn)
    conn_obj.set_conn()
    return conn_obj.get_conn(['engine', 'conn', 'metadata'])


@deprecated(deprecated_in='1.3.9', current_version=version, details='Use class Connection instead')
def get_raw_conn(db_conn: dict):
    conn_obj = DBClient(db_conn)
    conn_obj.set_raw_conn()
    return conn_obj.get_conn('conn')


@deprecated(deprecated_in='1.3.9', current_version=version, details='Use class Connection instead')
def get_sql(filename: str, encoding: str = 'utf-8'):
    """
    Get sql string from file
    :param filename: File name
    :param encoding: Encoding of file
    :return: String with sql
    """
    file = open(filename, 'r', encoding=encoding)
    sql = file.read()
    file.close()
    return sql


@deprecated(deprecated_in='1.3.9', current_version=version, details='Use class Connection instead')
def get_data(sql: str, db_conn, encoding: str = 'utf-8', print_script=False, **kwargs):
    conn_obj = DBClient(db_conn)
    if isinstance(db_conn, dict):
        conn_obj.set_conn()
    else:
        conn_obj.conn = db_conn
    ress = conn_obj.get_data(sql, encoding, print_script, **kwargs)

    return ress


@deprecated(deprecated_in='1.3.9', current_version=version, details='Use class Connection instead')
def get_data_row(sql: str, db_conn: dict, index: int = 0, encoding: str = 'utf-8', **kwargs):
    conn_obj = DBClient(db_conn)
    if isinstance(db_conn, dict):
        conn_obj.set_conn()
    else:
        conn_obj.conn = db_conn
    ress = conn_obj.get_data_row(sql, index, encoding, **kwargs)

    return ress


@deprecated(deprecated_in='1.3.9', current_version=version, details='Use class Connection instead')
def run_script(sql: str, db_conn: dict, encoding: str = 'utf-8', **kwargs):
    conn_obj = DBClient(db_conn)
    if isinstance(db_conn, dict):
        conn_obj.set_conn()
    else:
        conn_obj.conn = db_conn
    conn_obj.run_script(sql, encoding, **kwargs)


Connection = DBClient


if __name__ == '__main__':
    pass
