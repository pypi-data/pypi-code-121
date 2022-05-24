import pymysql

from re_common.baselibrary.database.moudle import SqlMoudle
from re_common.baselibrary.database.sql_factory import SqlFactory
from re_common.baselibrary.utils.version_compare import compare_bool

_json_escape_table = [chr(x) for x in range(128)]
_json_escape_table[0] = "\\0"
_json_escape_table[ord("\\")] = "\\\\"
_json_escape_table[ord("\n")] = "\\n"
_json_escape_table[ord("\r")] = "\\r"
_json_escape_table[ord("\032")] = "\\Z"
_json_escape_table[ord('"')] = '\\"'
_json_escape_table[ord("'")] = "\'"


class Mysql(SqlFactory):

    @property
    def db(self):
        # 就是conn
        if not self.is_ping():
            assert self._mysqlmoudle, AttributeError("MySQL model不存在 无法重新连接 请设置moudle")
            self.reConnect()
        return self._db  # type: pymysql.cursors.Cursor

    @db.setter
    def db(self, value):
        self._db = value

    @property
    def cursor(self):
        if self._cursor.connection:
            return self._cursor  # type: pymysql.cursors.Cursor
        else:
            self._cursor = self._db.cursor()
            return self._cursor

    @cursor.setter
    def cursor(self, value):
        self._cursor = value

    @property
    def mysqlmoudle(self):
        return self._mysqlmoudle  # type: SqlMoudle

    @mysqlmoudle.setter
    def mysqlmoudle(self, moudle):
        self._mysqlmoudle = moudle

    def get_new_cursor(self):
        """
        获取一个新的游标
        :return:
        """
        # 检查db的存在及是否断掉 不知道为什么 不可以加括号 但编辑器会警告
        return self._db.cursor()

    def link(self, mysqlmoudle: SqlMoudle):
        """
        连接数据库
        :param mysqlmoudle:
        :return:
        """
        self._mysqlmoudle = mysqlmoudle
        # 返回连接对象
        self._db = pymysql.connect(**mysqlmoudle.to_dict())
        self._cursor = self._db.cursor()

        return self

    def reConnect(self):
        """
        重新连接数据库
        :return:
        """
        try:
            self._db.ping()
            self._db.close()
        except:
            self.link(self._mysqlmoudle)
        self.link(self._mysqlmoudle)

    def is_ping(self):
        if self._db:
            try:
                return self._db.ping()
            except:
                self.link(self._mysqlmoudle)
        else:
            raise AttributeError("数据库连接对象不存在，请调用reConnect重新连接")

    def commit(self):
        """
        事务提交
        :return:
        """
        # 对象判断
        assert isinstance(self._db, pymysql.connections.Connection)
        self._db.commit()

    def execute(self, sql, args=None):
        """
        执行sql语句
        :param sql:
        :return:
        """
        try:
            assert isinstance(self._cursor, pymysql.cursors.Cursor)
            # 游标是否被关闭,执行该函数保证有游标
            self._cursor.execute(sql, args=args)
            self.commit()
        except Exception as e:
            raise e

    def fetchall(self):
        """
        select 后调用获取全部返回结果
        :return:
        """
        result = self._cursor.fetchall()
        return result

    def close(self):
        assert isinstance(self._db, pymysql.connections.Connection)
        self._db.close()

    def rollback(self):
        self.db.rollback()

    @classmethod
    def escape(cls, strings):
        # 这个不能用于多线程，否则会出现多线程抢占连接
        if compare_bool(pymysql.__version__, "1.0.0"):
            from pymysql.converters import escape_string
            return escape_string(strings)
        else:
            from pymysql import escape_string
            return escape_string(strings)

    def json_escape(self, strings):
        """
        json化需要
        :param strings:
        :return:
        """
        return strings.translate(_json_escape_table)

    def __repr__(self):
        return 'Mysql().link(%s)' % self._mysqlmoudle

    def __str__(self):
        return "Mysql %s" % self._mysqlmoudle

    def __del__(self):
        self.close()


def json_update(dicts):
    duplicte_list = []
    for k, v in dicts.items():
        if isinstance(v, str):
            duplicte_list.append(f"'$.{Mysql.escape(k)}','{Mysql.escape(v)}'")
        else:
            duplicte_list.append(f"'$.{Mysql.escape(k)}','{v}'")
    duplicte = ",".join(duplicte_list)
    # 处理 符合 %s 占位符里面的 正常数据非占位符存在 % 的情况
    duplicte_format = duplicte.replace("%", "%%")
    return duplicte_format
