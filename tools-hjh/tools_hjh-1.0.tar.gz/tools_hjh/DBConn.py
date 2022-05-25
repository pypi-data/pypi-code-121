# coding:utf-8
import os


class DBConn:
    """ 维护一个关系型数据库连接池，目前支持oracle，pgsql，mysql，sqlite；支持简单的sql执行 """

    def __init__(self, dbtype, host=None, port=None, db=None, user=None, pwd=None, poolsize=2, lib_dir=None):
        """ 初始化连接池
                如果是sqlite，db这个参数是要显示给入的
                如果是oracle，db给入的是sid或是servername都是可以的 """
        self.close()
        self.dbtype = dbtype
        config = {
            'host':host,
            'port':port,
            'database':db,
            'user':user,
            'password':pwd,
            'maxconnections':poolsize,  # 最大连接数
            'blocking':True,  # 连接数达到最大时，新连接是否可阻塞
            'reset':False
        }
        if self.dbtype == 'pgsql' or self.dbtype == 'mysql':
            from dbutils.pooled_db import PooledDB
        if self.dbtype == "pgsql":
            import psycopg2
            self.dbpool = PooledDB(psycopg2, **config)
        elif self.dbtype == "mysql":
            import pymysql
            self.dbpool = PooledDB(pymysql, **config)
        elif self.dbtype == "sqlite": 
            import sqlite3
            from dbutils.persistent_db import PersistentDB
            self.dbpool = PersistentDB(sqlite3, database=db)
        elif self.dbtype == "oracle":
            import cx_Oracle
            if lib_dir is not None:
                cx_Oracle.init_oracle_client(lib_dir=lib_dir)
            try:
                dsn = cx_Oracle.makedsn(host, port, service_name=db)
                self.dbpool = cx_Oracle.SessionPool(user=user,
                                                    password=pwd,
                                                    dsn=dsn,
                                                    max=poolsize,
                                                    increment=1,
                                                    encoding="UTF-8")
            except:
                dsn = cx_Oracle.makedsn(host, port, sid=db)
                self.dbpool = cx_Oracle.SessionPool(user=user,
                                                    password=pwd,
                                                    dsn=dsn,
                                                    max=poolsize,
                                                    increment=1,
                                                    encoding="UTF-8")
    
    def run(self, sql, param=None):
        """ 执行点什么
        sql中的占位符可以统一使用“?”
                如果param是一个字符串且作为文件路径判断存在则执行此文件
                如果param是list作为executemany第二个参数执行
                如果是一个元组作为execute第二个参数执行
                如果sql是select开头的，则返回col, rows，rows包含全部结果
        col表示列头组成的一个元组，rows是一个列表，由多个元组组成，每个元组是一行记录 """
        # 替换占位符
        if self.dbtype == 'pgsql' or self.dbtype == 'mysql':
            sql = sql.replace('?', '%s')
        elif self.dbtype == 'oracle':
            sql = sql.replace('?', ':1')            
        else:
            pass
        
        # 获取连接
        if self.dbtype == "oracle":
            conn = self.dbpool.acquire()
        else:
            conn = self.dbpool.connection()
            
        cur = conn.cursor()
                
        # 执行SQL文件
        if type(param) == str and os.path.exists(param):
            file = open(param)
            sqlStr = file.read()
            file.close()
            if self.dbtype == 'pgsql':
                cur.execute(sqlStr)
            elif self.dbtype == 'sqlite':
                cur.executescript(sqlStr)
            elif self.dbtype == 'mysql' or self.dbtype == 'oracle':
                pass  # 暂不支持
            conn.commit()
            cur.close()
            conn.close()
            return self
        
        # 执行非SELECT语句
        if not sql.lower().strip().startswith("select"):
            sql = sql.strip()
            if type(param) == list:
                cur.executemany(sql, param)
            elif type(param) == tuple:
                cur.execute(sql, param)
            elif param is None:
                cur.execute(sql)
            conn.commit()
            rownum = cur.rowcount
            cur.close()
            conn.close()
            return rownum
    
        # 执行SELECT语句
        if sql.lower().strip().startswith("select"):
            sql = sql.strip()
            col = []
            if param is None:
                cur.execute(sql)
            elif type(param) == tuple:
                cur.execute(sql, param)
            for c in cur.description:
                col.append(c[0])
            rows = cur.fetchall()
            cur.close()
            conn.close()
            return {'cols':tuple(col), 'rows':rows}
        
    def insert(self, table, rows):
        """ 往指定table中插入数据，rows是一个多个元组的列表，每个元组表示一组参数，或者是一个元组 """
        paramNum = '?'
        if type(rows) == list and len(rows) > 0:
            for _ in range(len(rows[0]) - 1):
                paramNum = paramNum + ', ?'
            sql = 'insert into ' + table + ' values(' + paramNum + ')' 
            num = self.run(sql, rows)
        elif type(rows) == tuple:
            for _ in range(len(rows) - 1):
                paramNum = paramNum + ', ?'
            sql = 'insert into ' + table + ' values(' + paramNum + ')' 
            num = self.run(sql, rows)
        return num
                
    def close(self):
        try:
            self.dbpool.close()
        except:
            pass
    
    def __del__(self):
        self.close()
        
