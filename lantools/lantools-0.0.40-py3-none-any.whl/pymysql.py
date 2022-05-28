import pymysql
from pymysql.cursors import DictCursor

class Mysql:
    def __init__(self, *, host, port, db, user, password, charset='utf8'):
        self._connect = pymysql.connect( host=host, port=port, db=db, user=user, password=password, charset=charset )
        self._cursor = self._connect.cursor(DictCursor)

    def ping(self):
        self._connect.ping(reconnect=True)

    def fetchall(self, sql, args=None):
        self.ping()
        self._cursor.execute(sql, args)
        self._connect.commit()
        return self._cursor.fetchall()

    def execute(self, sql, args=None):
        """ update, insert, delete """
        self.ping()
        self._cursor.execute(sql, args)
        self._connect.commit()

    def insert(self, sql, args=None):
        self.ping()
        self._cursor.execute(sql, args)
        id = self._cursor.lastrowid
        self._connect.commit()

        return id

    def __del__(self):
        self._connect.close()
