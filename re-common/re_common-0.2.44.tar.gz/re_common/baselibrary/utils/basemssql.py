import pymssql


class BaseMsSql(object):

    def __init__(self, host, user, pwd, db, charset, **kwargs):
        """
        as_dict  作为字典返回
        :param host:
        :param user:
        :param pwd:
        :param db:
        :param kwargs:
        """
        self.host = host
        self.user = user
        self.pwd = pwd
        self.db = db
        self.charset = charset
        self.kwargs = kwargs

    def conn(self):
        if not self.db:
            raise (NameError, "没有设置数据库信息")
        self.conn = pymssql.connect(host=self.host,
                                    user=self.user,
                                    password=self.pwd,
                                    database=self.db,
                                    charset=self.charset,
                                    **self.kwargs)
        self.cur = self.conn.cursor()
        if not self.cur:
            raise (NameError, "连接数据库失败")
        else:
            return self.cur

    def exec_select_query(self, sql):
        """
        执行查询语句
        返回的是一个包含tuple的list，list的元素是记录行，
        tuple的元素是每行记录的字段
        """
        try:
            self.cur.execute(sql)
            return self.cur
        except:
            self.close()

    def fetchone(self):
        """
        获取查询结果的下一行，返回一个元组，或者如果as_dict为True的话
        返回一个字典。如果没有更多可获取的数据了，返回None。
        如果前一个对execute*() 的调用没有产生任何结果集或者还没有提交调用，
        则抛出OperationalError
        :return:
        """
        return self.cur.fetchone()

    def fetchmany(self, size=None):
        """
        获取下一批查询结果，返回一个元组的列表，或者如果as_dict为True的话返回
        一个字典。如果没有更多可获取的数据了，返回一个空列表。
        你可以使用size参数调整之后每一批获取的行数，这个值会一直保留使用。
        如果前一个对execute*() 的调用没有产生任何结果集或者还没有提交调用，
        则抛出OperationalError
        :param size:
        :return:
        """
        return self.cur.fetchmany(size=size)

    def fetchall(self):
        """
        获取查询结果的所有剩余行，返回一个元组的列表，或者如果as_dict为True
        的话返回一个字典。如果没有更多可获取的数据了，返回一个空列表。
        如果前一个对execute*() 的调用没有产生任何结果集或者还没有提交调用，
        则抛出OperationalError
        :return:
        """
        return self.cur.fetchall()

    def exec_non_query(self, sql):
        """
        执行非查询语句
        """
        try:
            self.cur.execute(sql)
            self.conn.commit()
            return True
        except:
            self.close()
            return False

    def close(self):
        self.cur.close()
        self.conn.close()

    def __del__(self):
        self.close()
