# -*- coding: utf8 -*-
import MySQLdb
import time
import sys
import traceback


class StoreMysql(object):
    """
    mysql读写相关操作，需安装MySQLdb库
    Args:
        host:数据库ip
        user:数据库用户名
        password:数据库用户密码
        db:数据库名
        port:数据库端口，默认3306
        max_idle_time:数据库连接维持时间
        reconnect_interval:重连时间间隔
        reconnect_times:重连最大次数
        charset:数据库编码，默认utf8
    """
    def __init__(self, host="", user="", password="", db="", port=3306,
                 max_idle_time=7*3600, reconnect_interval=5, reconnect_times=360, charset="utf8"):
        self.host = host
        self.db = db
        self.max_idle_time = float(max_idle_time)
        self.reconnect_interval = reconnect_interval
        self.reconnect_times = reconnect_times
        args = dict(host=host, user=user, passwd=password, port=port, db=db,
                    use_unicode=True, charset=charset, init_command='SET names utf8')
        self._db = None
        self._db_args = args
        self._last_use_time = time.time()
        if not self.reconnect():
            print("Cannot connect to MySQL on %s" % self.host)

    def __del__(self):
        self.close()

    def close(self):
        if getattr(self, "_db", None) is not None:
            self._db.close()
            self._db = None

    @staticmethod
    def validate_connect(args):
        try:
            db = MySQLdb.connect(**args)
            return db
        except Exception:
            print(traceback.format_exc())
            return None

    def reconnect(self):
        self.close()
        try_time = 0
        status = False
        while not status and try_time < self.reconnect_times:
            try:
                self._db = MySQLdb.Connection(**self._db_args)
                return True
            except Exception:
                print(traceback.format_exc())
                time.sleep(self.reconnect_interval)
                status = False
            try_time += 1
        return status

    def _ensure_connected(self):
        if time.time() - self._last_use_time > self.max_idle_time:
            self.close()
        try_time = 0
        status = False
        while not status and try_time < self.reconnect_times:
            try:
                self._db.ping(True)
                status = True
            except Exception:
                print(traceback.format_exc())
                status = self.reconnect()
            try_time += 1
        self._last_use_time = time.time()

    def _cursor(self):
        self._ensure_connected()
        return self._db.cursor()

    def query(self, sql):
        """
        根据sql查询
        Returns：
            数组的数组，外层数组元素为一行，内存数组元素为一行的一列
        """
        rows = []
        cur = self._cursor()
        try:
            cur.execute(sql)
            self._db.commit()
            rows = cur.fetchall()
        except MySQLdb.OperationalError:
            print(traceback.format_exc())
            print("Error connecting to MySQL on {}; sql: {}".format(self.host, sql[0: 100]))
            rows = -1
        except Exception:
            print(traceback.format_exc())
            print("mysql query exception: sql: {}".format(sql[0: 100]))
            rows = -1
        finally:
            cur.close()
        return rows

    def count(self, tb):
        """
        返回某表的行数
        Args:
            tb:字符串，表名称
        """
        sql = 'select count(*) from %s' % tb
        results = self.query(sql)
        if len(results) == 1 and len(results[0]) == 1:
            return int(results[0][0])

    def do(self, sql, flag='lastrowid'):
        """
        执行sql，insert/delete/update操作
        Args:
            sql:要执行的sql
            flag:返回值类型，flag=lastrowid返回lastrowid，flag=rowcount返回rowcount
        """
        cur = self._cursor()
        r_data = None
        try:
            cur.execute(sql)
            self._db.commit()
            if flag == 'lastrowid':
                return cur.lastrowid
            elif flag == 'rowcount':
                return cur.rowcount
            r_data = 1
        except MySQLdb.OperationalError:
            print(traceback.format_exc())
            print("Error connecting to MySQL on {}; sql: {}".format(self.host, sql[0: 100]))
            r_data = -1
        except Exception:
            print(traceback.format_exc())
            print("mysql query exception: sql: {}".format(sql[0: 100]))
            r_data = -1
        finally:
            cur.close()
        return r_data

    def save(self, table, data, mapping_fields=dict()):
        """
        将字典直接insert到数据库
        Args:
            table:字符串，插入目标表的名称
            data:字典格式，key为字段名称，value为字段值，如{'id':'1','name':'temp'}
            mapping_fields: 用于保持data字典的key与数据库字段的对应关系，
                            如果结果字典的某个key不包含在mapping_fields中，则将直接使用key作为字段名
        """
        if len(data) <= 0:
            return -1
        try:
            fields = ''
            values = ''
            for d in data:
                if d in mapping_fields:
                    fields += "`%s`," % (str(mapping_fields[d]))
                else:
                    fields += "`%s`," % (str(d))
                values += "'%s'," % (str(data[d]))
            if len(fields) <= 0 or len(values) <= 0:
                return -1
            sql = "insert ignore into %s(%s) values(%s)" % (table, fields[:-1], values[:-1])
            return self.do(sql)
        except Exception:
            print(traceback.format_exc())
            return -1

    def update(self, table, data, field, mapping_fields=dict()):
        """
        将字典直接update到数据库
        Args:
            table:字符串，更新目标表的名称
            data:字典格式，key为字段名称，value为字段值，如{'id':'1','name':'temp'}
            field:唯一索引字段，即根据该字段判断是否为同一条记录，作为where条件
            mapping_fields: 用于保持data字典的key与数据库字段的对应关系，
                            如果结果字典的某个key不包含在mapping_fields中，则将直接使用key作为字段名
        """
        if len(data) <= 0:
            return -1
        else:
            try:
                values = ''
                field_value = None
                for d in data:
                    key = d
                    if d in mapping_fields:
                        key = mapping_fields[d]
                    if key == field:
                        field_value = data[d]
                    values += "%s='%s'," %(str(key),str(data[d]))
                if len(values) <= 0 or field_value is None:
                    return -1
                sql = "update " + table + " set " + values[:-1] + " where " + field + "='" + str(field_value) + "'"
                return self.do(sql, flag='rowcount')
            except Exception:
                print(traceback.format_exc())
                return -1

    def saveorupdate(self, table, data, field, mapping_fields=dict()):
        """
        将字典更新到数据库，如果已存在则update，不存在则insert
        Args:
            table:字符串，更新目标表的名称
            data:字典格式，key为字段名称，value为字段值，如{'id':'1','name':'temp'}
            field:唯一索引字段，即根据词字段判断是否为同一条记录，作为where条件
            mapping_fields: 用于保持data字典的key与数据库字段的对应关系，
                            如果结果字典的某个key不包含在mapping_fields中，则将直接使用key作为字段名
        """
        if len(data) <= 0:
            return -1
        try:
            field_value = None
            if field in data:
                field_value = data[field]
            else:
                for key in mapping_fields:
                    if mapping_fields[key] == field and key in data:
                        field_value = data[key]
            if field_value is None:
                return -1
            querysql = "select count(1) from " + table + " where " + field + "='" + str(field_value) + "'"
            ed = self.query(querysql)
            if ed and ed[0][0] > 0:
                return self.update(table, data, field, mapping_fields)
            else:
                return self.save(table, data, mapping_fields)
        except Exception:
            print(traceback.format_exc())
            return -1


def test():
    db = {
        'host': '182.254.159.210',
        'user': 'test',
        'password': 'pass',
        'db': 'e_business'
    }
    mq = StoreMysql(**db)
    print(mq.do('truncate user_copy', flag='rowcount'))

if __name__ == "__main__":
    test()

