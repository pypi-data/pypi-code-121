import warnings
from signal import SIGTERM, signal
from time import time

from click import echo, exceptions
from sqlalchemy import text


class RunStatement:
    """
    Mixin to handle SQL peculiarities
    """
    def flavor(self, conn):
        if conn.engine.name == 'postgresql':
            return 'postgresql'
        elif conn.engine.name.startswith("mysql"):
            return 'mysql'
        else:
            raise RuntimeError("Not supported DB engine: {}".format(conn.engine.name))

    def current_pid(self, connection):
        flv = self.flavor(connection)
        if flv == 'postgresql':
            (pid,) = connection.execute("SELECT pg_backend_pid()").fetchone()
        elif flv == 'mysql':
            (pid,) = connection.execute("SELECT connection_id()").fetchone()
        return pid

    def kill_pid(self, connection, pid):
        flv = self.flavor(connection)
        if flv == 'postgresql':
            connection.execute("pg_terminate_backend({0})".format(pid))
        elif flv == 'mysql':
            connection.execute("KILL {0}".format(pid))

    def prepare(self, connection, sql):
        if self.flavor(connection) == 'mysql':
            sql = sql.replace(":", "\\:")

        return sql

    def disable_fk_checks(self, connection):
        flv = self.flavor(connection)
        if flv == 'postgresql':
            for table in connection.engine.table_names():
                connection.execute(f"ALTER TABLE {table} DISABLE TRIGGER ALL")

        elif flv == 'mysql':
            connection.execute("SET FOREIGN_KEY_CHECKS = 0")

    def drop_table(self, connection, table):
        flv = self.flavor(connection)
        if flv == 'postgresql':
            connection.execute(f"DROP TABLE {table} CASCADE")
        elif flv == 'mysql':
            connection.execute(f"DROP TABLE {table}")

    def execute(self, connection, statements, warn=False):
        connection_id = self.current_pid(connection)
        result = None
        with warnings.catch_warnings():
            if not warn:
                warnings.simplefilter("ignore", category=Warning)
            try:
                for sql in statements:

                    sql = self.prepare(connection, sql)
                    yield "sql.statement.start", {"sql": sql, "script": self}
                    start_time = time()
                    result = connection.execute(text(sql))
                    yield "sql.statement.end", {
                        "sql": sql,
                        "script": self,
                        "time": time() - start_time,
                        "result": result,
                    }
            except (KeyboardInterrupt, exceptions.Abort) as ki:
                echo("🔫 Killing sql process {0} 🔫".format(connection_id))
                kill_conn = connection.engine.connect()
                self.kill_pid(kill_conn, connection_id)
                raise ki



def stopped(_a, _b):
    raise exceptions.Abort("Stopped")


signal(SIGTERM, stopped)
