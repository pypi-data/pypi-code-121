import sys
import traceback

import pypyodbc as pypyodbc


class BaseODBC(object):

    def __init__(self, MdbFile):
        self.connStr = r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};Dbq=%s;' % MdbFile
        self.mdbfile = MdbFile
        self.conn = None

    def conn_mdb(self):
        self.conn = pypyodbc.connect(self.connStr)
        return self

    def create_mdb(self):
        """
        创建一个文件，如果存在会保存
        :return:
        """
        pypyodbc.win_create_mdb(self.mdbfile)
        return self

    def get_tables(self):
        """
        获取表名
        :return:
        """
        # print(self.cur.tables())
        for table in self.cur.tables():
            yield table

    def get_description(self, sql):
        """
        获取查询结果的字段信息
        sql = "select * from `journal`"
        :param sql:
        :return:
        """

        self.cur.execute(sql)
        for row in self.cur.description:
            yield row

    def select_all(self, sql):
        """
        查询语句执行
        :param sql:
        :return:
        """
        self.cur.execute(sql)
        for row in self.cur.fetchall():
            yield row

    def select_yield(self, sql):
        """
        查询语句执行
        :param sql:
        :return:
        """
        for row in self.cur.execute(sql):
            yield row

    def get_cur(self):
        """
        获取游标
        :return:
        """
        self.cur = self.conn.cursor()
        return self.cur

    def excsql(self, sql, errExit=True):
        """
        执行sql
        :param sql:
        :param errExit:
        :return:
        """
        print(sql)
        try:
            self.cur.execute(sql)
            self.conn.commit()
        except:
            print(traceback.format_exc())
            if errExit:
                sys.exit(-1)

    def exc_list_sql(self, listsql, errExit=True):
        """
        传入一个sql的列表，循环执行
        :param listsql:
        :param errExit:
        :return:
        """
        for sql in listsql:
            print('input sql:' + sql)
            try:
                self.cur.execute(sql)
            except:
                print(traceback.format_exc())
                if errExit:
                    sys.exit(-1)
        self.conn.commit()

    def close_all(self):
        """
        关闭链接
        :return:
        """
        self.cur.close()
        self.conn.close()
