# db3数据的连接返回一个连接对象
import sys
import traceback

from re_common.baselibrary import MLogger
from re_common.baselibrary.baseabs import BaseAbs
from re_common.baselibrary.database.mbuilder import Sqlite3Builder


class Sqlite3Utiles(object):
    def __init__(self, logger=None):
        self.sqllite3 = None
        self.conn = None
        self.cursor = None

        self._logger = logger

    @property
    def logger(self):
        if self._logger is None:
            return MLogger().streamlogger
        return self._logger

    @logger.setter
    def logger(self, value):
        assert isinstance(value, MLogger)
        self._logger = value

    def get_new_cursor(self):
        """
        获取一个新的游标
        :return:
        """
        # 检查db的存在及是否断掉 不知道为什么 不可以加括号 但编辑器会警告
        return self.conn.cursor()

    def Sqlite3DBConnectFromFilePath(self, dbfilepath, encoding="gbk", timeout=60):
        """
        通过直接文件连接 我使用Hadoop导下来的db3是gbk编码的
        如果为utf-8编码请改为utf-8
        :param sec:  section
        :return:
        """
        sqllite3 = BaseAbs.get_sql_factory().sqlite_factory()
        # 传入的是配置文件和section选项 dbpath为配置文件路径
        sqlite3_moudle = Sqlite3Builder().build_file_path(dbfilepath).build_timeout(timeout).get_moudle()
        sqllite3.link(sqlite3_moudle)
        # 设置txt的编码格式  hadoop 上的db3为gbk 默认为utf8
        sqllite3.set_encoding(encoding=encoding)
        # 返回一个连接
        self.sqllite3 = sqllite3
        self.conn = self.sqllite3.db
        return self

    def Sqlite3DBConnectFromConfig(self, cobnfigfilepath, sec, encoding="gbk"):
        """
        通过配置文件连接
        :param sec:  section
        :return:
        """
        sqllite3 = BaseAbs.get_sql_factory().sqlite_factory()
        # 传入的是配置文件和section选项 dbpath为配置文件路径
        sqlite3_moudle = Sqlite3Builder(cobnfigfilepath, sec).build_all().get_moudle()
        sqllite3.link(sqlite3_moudle)
        # 设置txt的编码格式  hadoop 上的db3为gbk 默认为utf8
        sqllite3.set_encoding(encoding=encoding)
        # 返回一个连接
        self.sqllite3 = sqllite3
        self.conn = self.sqllite3.db
        return self

    def ExeSqlliteList(self, sqlList, errExit=True):
        """
        该函数和上面一样执行一个sql列表且不返回结果
        属于插入和更新类函数 但该函数针对db3
        :param sqllitename:
        :param sqlList:
        :return:
        """
        dbMsg = None
        cur = self.get_new_cursor()
        if self.conn:
            count = 0
            for sql in sqlList:
                count += 1
                try:
                    self.logger.info("{} 执行sql数量:{}".format(sql, str(count)))
                    cur.execute(sql)
                except:
                    self.logger.error('*errSql:' + sql)
                    dbMsg = '*InsertError:' + traceback.format_exc()
                    if errExit:
                        self.logger.error(dbMsg)
                        sys.exit()
                if dbMsg:
                    self.logger.error(dbMsg)
                    continue
        self.conn.commit()
        cur.close()

    def ExeSqlliteMany(self, sql, itermany, errExit=True):
        dbMsg = None
        cur = self.get_new_cursor()
        if self.conn:
            try:
                self.logger.info("{}\n{}".format(sql, str(itermany)))
                cur.executemany(sql, itermany)
            except:
                self.logger.error('*errSql:' + sql)
                dbMsg = '*InsertError:' + traceback.format_exc()
                if errExit:
                    self.logger.error(dbMsg)
                    sys.exit()
            if dbMsg:
                self.logger.error(dbMsg)
        self.conn.commit()
        cur.close()

    def ExeSqlliteSql(self, sql):
        """
        该函数和上面一样执行一个sql列表且不返回结果
        属于插入和更新类函数 但该函数针对db3
        :param sqllitename:
        :param sqlList:
        :return:
        """
        dbMsg = None
        cur = self.get_new_cursor()
        if self.conn:
            try:
                self.logger.info(sql)
                cur.execute(sql)
                self.conn.commit()
            except:
                self.logger.error('*errSql:' + sql)
                dbMsg = '*InsertError:' + traceback.format_exc()
            if dbMsg:
                self.logger.error(dbMsg)
                return False
        else:
            return False
        cur.close()
        return True

    def SelectFromSqlliteFetchall(self, sql):
        """
        该函数和上面一样执行一个sql列表且不返回结果
        属于插入和更新类函数 但该函数针对db3
        :param sqllitename:
        :param sqlList:
        :return:
        """
        cur = self.get_new_cursor()
        if self.conn:
            try:
                self.logger.info(sql)
                cur.execute(sql)
                rows = cur.fetchall()
                return rows
            except:
                self.logger.error('*errSql:' + sql)
                dbMsg = '*InsertError:' + traceback.format_exc()
            if dbMsg:
                self.logger.error(dbMsg)
                return False
        else:
            return False
        cur.close()

    def SelectFromSqlliteFetchall_dicts(self, sql):
        """
        该函数和上面一样执行一个sql列表且不返回结果
        属于插入和更新类函数 但该函数针对db3
        :param sqllitename:
        :param sqlList:
        :return:
        """

        def dict_factory(cursor, row):
            d = {}
            for idx, col in enumerate(cursor.description):
                d[col[0]] = row[idx]
            return d

        self.conn.row_factory = dict_factory
        cur = self.get_new_cursor()
        if self.conn:
            try:
                self.logger.info(sql)
                cur.execute(sql)
                rows = cur.fetchall()
                return rows
            except:
                self.logger.error('*errSql:' + sql)
                dbMsg = '*InsertError:' + traceback.format_exc()
            if dbMsg:
                self.logger.error(dbMsg)
                return False
        else:
            return False
        cur.close()

    def SelectFromSqlliteFetchOne(self, sql):
        """
        该函数和上面一样执行一个sql列表且不返回结果
        属于插入和更新类函数 但该函数针对db3
        :param sqllitename:
        :param sqlList:
        :return:
        """
        dbMsg = None
        cur = self.get_new_cursor()
        if self.conn:
            try:
                self.logger.info(sql)
                cur.execute(sql)
                while True:
                    row = cur.fetchone()
                    if row is None:
                        return None
                    else:
                        yield row
            except:
                self.logger.error('*errSql:' + sql)
                dbMsg = '*InsertError:' + traceback.format_exc()
            if dbMsg:
                self.logger.error(dbMsg)
                return False
        else:
            return False
        cur.close()

    def ExeVACUUM(self):
        """
        清理空间
        :return:
        """
        dbMsg = None
        if self.conn:
            try:
                self.conn.execute("VACUUM")
            except:
                dbMsg = '*VACUUMError:' + traceback.format_exc()
            if dbMsg:
                self.logger.error(dbMsg)
                return False
        else:
            return False
        return True

    def sqliteEscape(self, keyWord):
        keyWord = keyWord.replace("'", "''")
        keyWord = keyWord.replace("\\", "\\\\")
        return keyWord

    def close(self):
        self.conn.close()
