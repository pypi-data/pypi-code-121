import traceback
import psycopg2
import pymssql
import logging
from decimal import Decimal


class RDBService:
    def __init__(self, database):
        self.conn = None
        self.database = database

    def connect(self):
        self.__connect()

    def __connect(self):
        if self.conn is not None:
            return
        if self.database.type == 'mssql':
            self.conn = pymssql.connect(server=self.database.host,
                                        port=self.database.port,
                                        user=self.database.account,
                                        database=self.database.database,
                                        password=self.database.password)
        elif self.database.type == 'mysql':
            self.conn = pymssql.connect(server=self.database.host,
                                        port=self.database.port,
                                        user=self.database.account,
                                        database=self.database.database,
                                        password=self.database.password)
        elif self.database.type == 'postgresql':
            self.conn = psycopg2.connect(host=self.database.host,
                                         port=self.database.port,
                                         user=self.database.account,
                                         database=self.database.database,
                                         password=self.database.password)
        else:
            raise (NameError, "Unsupported!")

    def close(self):
        if self.conn != None:
            try:
                self.conn.close()
            finally:
                self.conn = None
                logging.info('Close the connnection with server.')

    # 向${collection}表新增一条记录${data}
    def insert(self, table, data):
        try:
            if self.conn is None:
                self.__connect()
            fields = []
            values = []
            for key in data:
                fields.append(key)
                values.append(self.__toValue(data[key]))
            sql = 'insert into {} ({}) values ({})'.format(table, ','.join(fields), ','.join(values))
            cusor = self.conn.cursor()
            cusor.execute(sql)
            self.conn.commit()
            cusor.close()
            # logging.debug("New a record into {}: {}".format(table, data))
        except Exception as e:
            traceback.print_exc()
            logging.warning('while excute insert new data({}) in {}'.format(table, data))
            self.close()
            raise e

    # 根据${query}查找一条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    """

    def find_one(self, table, query, sort=None, fields=None):
        raise (NameError, "Unsupported")

    # 根据${query}查找多条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    sort : 'order by ${fields} ${asc|desc}
    page_site: 分页大小 
    """

    def find(self, table, query, sort, fields, limit=None):
        raise (NameError, "Unsupported")

    # 根据${query}分页查找多条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    sort : 'order by ${fields} ${asc|desc}
    page_size: 分页大小 
    page_number: 第几页
    """

    def findWithPages(self, table, query, sort, fields, page_number=1, page_size=10):
        raise (NameError, "Unsupported")

    """
    更新最先匹配filter的所有记录
    update: {${field}:${value}}
    """

    def update(self, table, query, update):
        try:
            if self.conn is None:
                self.__connect()
            expressions = []
            for key in update:
                expressions.append("{}={}".format(key, self.__toValue(update[key])))
            update_str = ",".join(expressions)
            sql = 'update {} set {} {}'.format(table, update_str, query)
            cusor = self.conn.cursor()
            cusor.execute(sql)
            self.conn.commit()
            cusor.close()

        except Exception as e:
            traceback.print_exc()
            logging.warning('while excute updating({}) sql with query({}) in {}'.format(update, table, query))
            self.close()
            raise e

    def delete(self, table, query):
        try:
            if self.conn is None:
                self.__connect()
            sql = 'delete from {} {}'.format(table, query)
            cusor = self.conn.cursor()
            res = cusor.execute(sql)
            self.conn.commit()
            cusor.close()
            # logging.debug('数据删除成功！')
        except Exception as e:
            traceback.print_exc()
            logging.warning('while excute deleting sql with query({}) in {}'.format(table, query))
            self.close()
            raise e

    def count(self, table, query):
        try:
            if self.conn is None:
                self.__connect()
            countSql = 'select count(*) from {} {}'.format(table, query)
            cusor = self.conn.cursor()

            count = cusor.execute(countSql)
            count = cusor.fetchall()
            cusor.close()


        except Exception as e:
            traceback.print_exc()
            logging.warning('while excute counting sql with query({}) in {}'.format(table, query))
            self.close()
            raise e

    def __toValue(self, var):
        if isinstance(var, int) or isinstance(var, float):
            return str(var)
        elif isinstance(var, Decimal):
            # return str(round(var,2))
            return str(var)
        else:
            return '\'{}\''.format(var)

    @staticmethod
    def createRDBService(database):
        if database.type == 'mssql':
            return MssqlService(database)
        elif database.type == 'mysql':
            return MysqlService(database)
        elif database.type == 'postgresql':
            return PostgresqlService(database)
        else:
            raise (NameError, "Unsupported database type: {}".format(database.type))


class MssqlService(RDBService):
    def __init__(self, database):
        super().__init__(database)

    def __connect(self):
        super.connnect()

    def __close(self):
        super().close()

    # 根据${query}查找一条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    """

    def find_one(self, table, query, sort=None, fields=None):
        try:
            self.__connect()
            s = '*'

            if fields is not None:
                s = ','.join(fields)

            sql = 'select top 1 {} from {} {} {}'.format(s, table, query if query is not None else '',
                                                         sort if sort is not None else '')
            cusor = self.conn.cursor()
            if not cusor:
                raise (NameError, "连接数据库失败")
            else:
                res = cusor.execute(sql)
                res = cusor.fetchall()
                cusor.close()
                return res[0] if len(res) > 0 else None
        except Exception as e:
            self.close()
            logging.warning('while excute find_one sql with query({}) in {}'.format(table, query))
            raise e

    # 根据${query}查找多条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    sort : 'order by ${fields} ${asc|desc}
    page_size: 分页大小
    """

    def find(self, table, query, sort, fields, limit=None):
        try:
            self.__connect()
            topN = '' if limit is None else 'top {}'.format(limit)
            if fields is None:
                sql = 'select {} * from {} {} {}'.format(topN, table, query if query is not None else '',
                                                         sort if sort is not None else '')
            else:
                sql = 'select {} {} from {} {} {}'.format(topN, ','.join(fields), table,
                                                          query if query is not None else '',
                                                          sort if sort is not None else '')
            cusor = self.conn.cursor()
            if not cusor:
                raise (NameError, "连接数据库失败")
            else:
                cusor.execute(sql)
                result = cusor.fetchall()
                cusor.close()

                # return {'total': count, 'result': result}
                return result
        except Exception as e:
            self.close()
            logging.warning('while excute find sql with query({}) in {}'.format(table, query))
            raise e

    def findWithPages(self, table, query, sort, fields, page_number=1, page_size=10):
        try:
            self.__connect()

            page_params = '' if page_number is None or page_size is None \
                else 'offset {} rows fetch next {} rows only'.format((page_number-1) * page_size, page_size)
            if fields is None:
                sql = 'select * from {} {} {} {}'.format(table, query if query is not None else '',
                                                         sort if sort is not None else '', page_params)
            else:
                sql = 'select {} from {} {} {} {}'.format(','.join(fields), table, query if query is not None else '',
                                                          sort if sort is not None else '', page_params)
            cusor = self.conn.cursor()
            if not cusor:
                raise (NameError, "连接数据库失败")
            else:
                cusor.execute(sql)
                result = cusor.fetchall()
                cusor.close()

                # return {'total': count, 'result': result}
                return result
        except Exception as e:
            self.close()
            logging.warning('while excute find sql with query({}) in {}'.format(table, query))
            raise e


class MysqlService(RDBService):
    def __init__(self, settings):
        super().__init__(settings)

    def __connect(self):
        super().connect()

    def __close(self):
        super().close()

    # 根据${query}查找一条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    """

    def find_one(self, table, query, sort=None, fields=None):
        try:
            self.__connect()
            s = '*'

            if fields is not None:
                s = ','.join(fields)

            sql = 'select {} from {} {} {} limit 1'.format(s, table, query if query is not None else '',
                                                           sort if sort is not None else '')
            cusor = self.conn.cursor()
            res = cusor.execute(sql)
            res = cusor.fetchall()
            cusor.close()
            return res[0] if len(res) > 0 else None
        except Exception as e:
            self.__close()
            logging.warning('while excute find_one sql with query({}) in {}'.format(table, query))
            raise e

    # 根据${query}查找多条记录
    """
    query = "where a=b or (c like 'd')" sql子句
    sort : 'order by ${fields} ${asc|desc}
    page_site: 分页大小 
    """

    def find(self, table, query, sort, fields, limit=None):
        try:
            self.__connect()

            topN = '' if limit is None else 'limit {}'.format(limit)
            if fields is None:
                sql = 'select  * from {} {} {} {}'.format(table, query if query is not None else '',
                                                          sort if sort is not None else '', topN)
            else:
                sql = 'select {} from {} {} {} {}'.format(','.join(fields), table, query if query is not None else '',
                                                          sort if sort is not None else '', topN)
            cusor = self.conn.cursor()
            result = cusor.execute(sql)
            result = cusor.fetchall()
            cusor.close()

            # return {'total': count,'result': result}
            return result
        except Exception as e:
            self.__close()
            logging.warning('while excute find sql with query({}) in {}'.format(table, query))
            raise e

    def findWithPages(self, table, query, sort, fields, page_number=1, page_size=10):
        try:
            self.__connect()
            page_params = '' if page_number is None or page_size is None \
                else 'limit {} offset {}'.format(page_size,(page_number-1) * page_size)
            if fields is None:
                sql = 'select * from {} {} {} {}'.format(table, query if query is not None else '',
                                                         sort if sort is not None else '', page_params)
            else:
                sql = 'select {} from {} {} {} {}'.format(','.join(fields), table, query if query is not None else '',
                                                          sort if sort is not None else '', page_params)
            cusor = self.conn.cursor()
            if not cusor:
                raise (NameError, "连接数据库失败")
            else:
                cusor.execute(sql)
                result = cusor.fetchall()
                cusor.close()

                # return {'total': count, 'result': result}
                return result
        except Exception as e:
            self.close()
            logging.warning('while excute find sql with query({}) in {}'.format(table, query))
            raise e

class PostgresqlService(MysqlService):
    def __init__(self, settings):
        super().__init__(settings)

    def __connect(self):
        super().connect()

    def __close(self):
        super().close()
