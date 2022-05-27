# coding:utf-8
import os
from tools_hjh import other as tools


class DBConn:
    """ 维护一个关系型数据库连接池，目前支持oracle，pgsql，mysql，sqlite；支持简单的sql执行 """

    def __init__(self, dbtype, host=None, port=None, db=None, user=None, pwd=None, poolsize=2, lib_dir=None):
        """ 初始化连接池
                如果是sqlite，db这个参数是要显示给入的
                如果是oracle，db给入的是sid或是servername都是可以的 """
        self.dbpool = None
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
        finally:
            self.dbpool = None
    
    def __del__(self):
        self.close()
        
        
class oracletools:
    """ 用于Oracle的工具类 """

    @staticmethod
    def desc(db, user, table):
        """ 类似于sqlplus中的desc命令 """
        user = user.upper()
        table = table.upper()
        sql = '''
            select column_name, 
                case 
                    when data_type = 'VARCHAR2' or data_type = 'CHAR' or data_type = 'VARCHAR' then 
                        data_type || '(' || data_length || ')'
                    when data_type = 'NUMBER' and data_precision > 0 and data_scale > 0 then 
                        data_type || '(' || data_precision || ', ' || data_scale || ')'
                    when data_type = 'NUMBER' and data_precision > 0 and data_scale = 0 then 
                        data_type || '(' || data_precision || ')'
                    when data_type = 'NUMBER' and data_precision = 0 and data_scale = 0 then 
                        data_type
                    else data_type 
                end column_type
            from dba_tab_cols where owner = ? and table_name = ? and column_name not like '%$%' order by column_id
        '''
        tab = ''
        cols_ = db.run(sql, (user, table))[1]
        lenNum = 0
        for col_ in cols_:
            if lenNum < len(col_[0]):
                lenNum = len(col_[0])
        for col_ in cols_:
            tablename = col_[0]
            typestr = col_[1]
            spacesnum = lenNum - len(tablename) + 1
            colstr = tablename + ' ' * (spacesnum) + typestr
            tab = tab + colstr + '\n'
        return tab
    
    @staticmethod
    def get_ddl(db, user, table):
        """ 需要dba权限，得到目标user.table的单元性的建表语句，包括约束，索引和注释等 """
        user = user.upper()
        table = table.upper()
        rssqls = []
        # 建表
        rssqls.append('create table ' + user + '.' + table + '(test_col number)')
        # 按顺序建列
        sql = '''
            select column_name, 
                case 
                    when data_type = 'VARCHAR2' or data_type = 'CHAR' or data_type = 'VARCHAR' or data_type = 'NVARCHAR2' then 
                        data_type || '(' || data_length || ')'
                    when data_type = 'NUMBER' and data_precision > 0 and data_scale > 0 then 
                        data_type || '(' || data_precision || ', ' || data_scale || ')'
                    when data_type = 'NUMBER' and data_precision > 0 and data_scale = 0 then 
                        data_type || '(' || data_precision || ')'
                    when data_type = 'NUMBER' and data_precision = 0 and data_scale = 0 then 
                        data_type
                    else data_type 
                end column_type
            from dba_tab_cols where owner = ? and table_name = ? and column_name not like '%$%' order by column_id
        '''
        for r in db.run(sql, (user, table))[1]:
            rssqls.append('alter table ' + user + '.' + table + ' add ' + r[0] + ' ' + r[1].strip())
        rssqls.append('alter table ' + user + '.' + table + ' drop column test_col')
        # 建主键
        sql = '''
            select t.constraint_name, to_char(wm_concat(t2.column_name)) cols
            from dba_constraints t, dba_cons_columns t2
            where t.owner = ?
            and t.table_name = ?
            and t.constraint_name = t2.constraint_name
            and t.table_name = t2.table_name
            and t.constraint_type = 'P'
            group by t.constraint_name
        '''
        for r in db.run(sql, (user, table))[1]:
            rssqls.append('alter table ' + user + '.' + table + ' add constraint ' + r[0] + ' primary key(' + r[1] + ')')
        # 建非空约束
        sql = '''
            select t.search_condition
            from dba_constraints t, dba_cons_columns t2
            where t.owner = ?
            and t.table_name = ?
            and t.constraint_name = t2.constraint_name
            and t.table_name = t2.table_name
            and t.constraint_type = 'C'
            and t.search_condition is not null
        '''
        for r in db.run(sql, (user, table))[1]:
            if 'IS NOT NULL' in r[0]:
                col = r[0].split(' ')[0]
                rssqls.append('alter table ' + user + '.' + table + ' modify ' + col + ' not null')
        # 建唯一约束
        sql = '''
            select t.constraint_name, to_char(wm_concat(t2.column_name)) cols
            from dba_constraints t, dba_cons_columns t2
            where t.owner = ?
            and t.table_name = ?
            and t.constraint_name = t2.constraint_name
            and t.table_name = t2.table_name
            and t.constraint_type = 'U'
            group by t.constraint_name
        '''
        for r in db.run(sql, (user, table))[1]:
            rssqls.append('alter table ' + user + '.' + table + ' add constraint ' + r[0] + ' unique(' + r[1] + ')')
        # 建默认值
        sql = '''
            select column_name, data_default
            from dba_tab_columns
            where owner = ? 
            and table_name = ? 
            and column_name not like '%$%'
            and data_default is not null
        '''
        for r in db.run(sql, (user, table))[1]:
            rssqls.append('alter table ' + user + '.' + table + ' modify ' + r[0] + ' default ' + r[1].strip())
        # 建普通索引
        sql = '''
            select t.index_name, to_char(wm_concat(t2.column_name)) cols
            from dba_indexes t, dba_ind_columns t2
            where t.owner = ? 
            and t.table_name = ? 
            and t.index_name = t2.index_name
            and t.owner = t2.table_owner
            and t.uniqueness = 'NONUNIQUE'
            and t.index_type = 'NORMAL'
            group by t.index_name
        '''
        for r in db.run(sql, (user, table))[1]:
            rssqls.append('create index ' + user + '.' + r[0] + ' on ' + user + '.' + table + '(' + r[1] + ')')
        # 建函数索引
        sql = '''
            select t.index_name, t3.column_expression
            from dba_indexes t, dba_ind_expressions t3
            where t.owner = ? 
            and t.table_name = ? 
            and t.index_name = t3.index_name
            and t.table_name = t3.table_name
            and t.owner = t3.table_owner
            and t.uniqueness = 'NONUNIQUE'
            and t.index_type = 'FUNCTION-BASED NORMAL'
            order by t3.column_position
        '''
        col, rows = db.run(sql, (user, table))
        mdb = MemoryDB()
        mdb.set('t_idx', col, rows)
        rs = mdb.db.run('select index_name, group_concat(column_expression) from t_idx group by index_name')[1]
        mdb.close()
        for r in rs:
            rssqls.append('create index ' + user + '.' + r[0] + ' on ' + user + '.' + table + '(' + r[1] + ')')
        # 建注释
        sql = '''
            select column_name, comments
            from dba_col_comments
            where owner = ? 
            and table_name = ? 
            and comments is not null
        '''
        for r in db.run(sql, (user, table))[1]:
            rssqls.append("comment on column " + user + "." + table + "." + r[0] + " is '" + r[1] + "'")
        # 建外键
        pass
        return rssqls
    
    @staticmethod
    def get_dbms_ddl(db, user, table):
        """ 得到目标user.table的的建表语句，直接调用dbms_metadata.get_ddl得到结果 """
        user = user.upper()
        table = table.upper()
        sql = '''
            select to_char(
                dbms_metadata.get_ddl('TABLE', ?, ?)
            ) from dual
        '''
        return db.run(sql, (table, user))[1][0]
    
    @staticmethod
    def compare_table(srcdb, srcuser, dstdb, dstuser):
        """ 比较两个不同用户下同名表表结构，输出不一致的表清单，和一段报告 """
        srcuser = srcuser.upper()
        dstuser = dstuser.upper()
        out = ''
        tablist = []
        sql = 'select table_name from dba_tables where owner = ?'
        srctabs = srcdb.run(sql, (srcuser,))[1]
        for tab in srctabs:
            srcdesc = OracleTools.desc(srcdb, srcuser, tab[0])
            dstdesc = OracleTools.desc(dstdb, dstuser, tab[0])
            if srcdesc != dstdesc:
                tablist.append(tab[0])
                out = out + tools.linemergealign(srcuser + '.' + tab[0] + '\n' + srcdesc
                                           , dstuser + '.' + tab[0] + '\n' + dstdesc
                                           , True) + '\n\n'
        return tablist, out
    
    @staticmethod
    def sync_table(srcdb, srcuser, dstdb, dstuser, table, mode=1):
        """ 同步表，mode：
        0：仅输出增量同步表结构的sql
        1：增量同步表结构
        2：重建表结构，不包含外键
        3：重建表，且同步数据 """
        report = ''
        if mode == 0:
            sqls = OracleTools.get_ddl(srcdb, srcuser, table)
            for sql in sqls:
                sql = sql.replace(srcuser + '.', dstuser + '.')
                report = report + sql + ';\n'
        if mode == 1:
            sqls = OracleTools.get_ddl(srcdb, srcuser, table)
            for sql in sqls:
                sql = sql.replace(srcuser + '.', dstuser + '.')
                try:
                    dstdb.run(sql)
                    report = report + 'ok:' + sql + '\n'
                except:
                    report = report + 'err:' + sql + '\n'
        if mode == 2:
            try:
                sql = 'drop table ' + dstuser + '.' + table
                dstdb.run(sql)
                report = report + 'ok:' + sql + '\n'
            except:
                report = report + 'err:' + sql + '\n'
            sqls = OracleTools.get_ddl(srcdb, srcuser, table)
            for sql in sqls:
                sql = sql.replace(srcuser + '.', dstuser + '.')
                dstdb.run(sql)
                report = report + 'ok:' + sql + '\n'
        if mode == 3:
            try:
                sql = 'drop table ' + dstuser + '.' + table + ' cascade constraints purge'
                # dstdb.run(sql)
                report = report + 'ok:' + sql + '\n'
                
            except:
                report = report + 'err:' + sql + '\n'
            sqls = OracleTools.get_ddl(srcdb, srcuser, table)
            for sql in sqls:
                sql = sql.replace(srcuser + '.', dstuser + '.')
                try:
                    # dstdb.run(sql)
                    report = report + 'ok:' + sql + '\n'
                except:
                    report = report + 'err:' + sql + '\n'
            sql = 'select * from ' + srcuser + '.' + table
            conn = srcdb.dbpool.acquire()
            cur = conn.cursor()
            cur.execute(sql)
            while True:
                rs = cur.fetchone()
                if rs is not None:
                    pa = str(rs)
                    sql = 'insert into ' + dstuser + '.' + table + ' values' + pa
                    # dstdb.run(sql)
                    print(sql)
                else:
                    break
            cur.close()
            conn.close()
        return report


class MemoryDB: 
    """ 维护一个:memory:方式打开的sqlite数据库连接 """

    def __init__(self):
        self.db = DBConn('sqlite', db=':memory:')
        
    def set(self, tablename, col, rows):
        """ 重建指定表，且插入rows数据 """
        sql1 = 'drop table if exists ' + tablename
        sql2 = 'create table ' + tablename + ' ('
        for col_ in col:
            sql2 = sql2 + col_ + ' text, \n'
        sql2 = sql2.strip().strip(',') + ')'
        self.db.run(sql1)
        self.db.run(sql2)
        return self.db.insert(tablename, rows)
    
    def append(self, tablename, rows):
        """ 往指定表插入rows数据 """
        return self.db.insert(tablename, rows)
        
    def get(self, tablename):
        """ 得到指定表全部数据（col,rows） """
        sql = 'select * from ' + tablename
        return self.db.run(sql)
    
    def close(self):
        self.db.close()

    def __del__(self):
        self.close()
      

