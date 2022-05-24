import sqlite3

from re_common.baselibrary.database.moudle import Sqlite3Moudle
from re_common.baselibrary.database.sql_factory import SqlFactory
from re_common.baselibrary.utils.basedict import BaseDicts


def dict_factory(cursor, row):
    """
    设置返回字典
    :param row:
    :return:
    """
    d = {}
    for index, col in enumerate(cursor.description):
        d[col[0]] = row[index]
    return d


class Sqlite3(SqlFactory):
    def __init__(self):
        # 就是conn
        self.db = ''
        self.cursor = ''
        self.sqlite3_moudle = {}

    def set_result_dict(self):
        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.db.row_factory = dict_factory
        self.get_cursor()
        return self

    def set_encoding(self, bytes=False, encoding="gbk"):
        """
        https://blog.csdn.net/xkxjy/article/details/8179479
        在不知道编码格式的情况下 使用bytes 但我没有成功
        :param bytes:
        :param encoding:
        :return:
        """
        # if bytes:
        #     self.db.text_factory = bytes
        # else:
        #     self.db.text_factory = lambda x: str(x, encoding, 'ignore')
        self.db.text_factory = lambda x: str(x, encoding, 'ignore')

    def link(self, sqlite3_moudle: Sqlite3Moudle):
        """
        连接数据库
        :param sqlite3_moudle:
        :param mysqlmoudle:
        :return:
        """
        self.sqlite3_moudle = sqlite3_moudle
        # 返回连接对象
        dicts = sqlite3_moudle.to_dict()
        dicts = BaseDicts.removeDictsNone(dicts)
        self.db = sqlite3.connect(**dicts)
        self.cursor = self.db.cursor()
        return self.db, self.cursor

    def get_cursor(self) -> sqlite3.Cursor:
        """
        本函数通过链接返回sqlite3的游标
        :param connect: 传入的是sqlite3的连接
        :return: 返回游标
        """
        assert isinstance(self.db, sqlite3.Connection)
        self.cursor = self.db.cursor()
        return self.cursor

    def execute(self, sql: str) -> sqlite3.Cursor:
        """
        通过游标对象执行sql语句并返回结果
        :param cursor: 游标对象
        :param sql:  需要执行的sql语句
        :return:  返回结果的游标对象
        """
        assert isinstance(self.cursor, sqlite3.Cursor)
        result = self.cursor.execute(sql)
        return result

    def executemany(self, sql: str, seq_of_parameters) -> sqlite3.Cursor:
        assert isinstance(self.cursor, sqlite3.Cursor)
        result = self.cursor.executemany(sql, seq_of_parameters)
        return result

    def get_all_field_info(self, tablename):
        """
        获取字段详细信息
        :param tablename:
        :return:
        """
        sql = "PRAGMA table_info({})".format(tablename)
        result = self.execute(sql)
        return result.fetchall()

    def get_all_field(self, tablename):
        """
        仅仅获取字段
        :param tablename:
        :return:
        """
        listinfo = self.get_all_field_info(tablename)
        return [row[1] for row in listinfo]

    def get_table_name(self):
        """
        获取表名
        :return:
        """
        sql = "select name from sqlite_master where type='table' order by name;"
        result = self.execute(sql)
        return result.fetchall()

    def get_rowcount(self, ) -> int:
        """
        获取sql语句影响的行数
        :param cursor: 游标对象
        :return:  影响的行数
        """
        assert isinstance(self.cursor, sqlite3.Cursor)
        num = self.cursor.rowcount
        return num

    def close_cursor(self) -> None:
        """
        关闭游标
        :param cursor: 游标
        :return: None
        """
        assert isinstance(self.cursor, sqlite3.Cursor)
        self.cursor.close()

    def my_commit(self) -> None:
        """
        提交
        :param connect: 连接
        :return: None
        """
        assert isinstance(self.db, sqlite3.Connection)
        self.db.commit()

    def close_connect(self) -> None:
        """
        链接关闭
        :param connect: 连接
        :return: None
        """
        assert isinstance(self.db, sqlite3.Connection)
        self.db.close()

    def __del__(self):
        self.close_connect()

    @classmethod
    def sqlite3_merge(cls, inpath, attachpath, tablename="modify_title_info_zt"):
        """
        合并两个db3
        :param inpath:
        :param attachpath:
        :return:
        """
        conn = sqlite3.connect(inpath)
        conn.text_factory = str
        cur = conn.cursor()
        attach = 'attach database "' + attachpath + '" as w;'
        sql1 = 'insert into {} select * from w.{};'.format(tablename, tablename)
        cur.execute(attach)
        cur.execute(sql1)
        conn.commit()
        cur.close()
        conn.close()

    def create_table(self, tablename, fields: list):
        if self.cursor == '':
            self.get_cursor()
        sql = "PRAGMA foreign_keys = false;"
        self.execute(sql)
        sql = f'DROP TABLE IF EXISTS "{tablename}";'
        self.execute(sql)
        strings = ""
        for field in fields:
            strings = strings + f'"{field}" TEXT,'
        strings = strings.rstrip(',')
        sql = f'CREATE TABLE "{tablename}"({strings});'
        self.execute(sql)
        sql = 'PRAGMA foreign_keys = true;'
        self.execute(sql)
