from re_common.baselibrary.baseabs import BaseAbs


class SqlFactory(BaseAbs):
    """
    sql 工厂类
    """
    @staticmethod
    def mysql_factory(type='mysql'):
        if type == 'mysql':
            """
            mysql类 返回一个mysql的对象
            """
            from re_common.baselibrary.database.mysql import Mysql
            return Mysql()
        assert 0, "err sql type please check: %s" % type

    @staticmethod
    def sqlite_factory(type='sqlite3'):
        if type == 'sqlite3':
            """
             sqlite3类 返回一个sqlite3的对象
             """
            from re_common.baselibrary.database.msqlite3 import Sqlite3
            return Sqlite3()
        assert 0, "err sqllite type please check: %s" % type
