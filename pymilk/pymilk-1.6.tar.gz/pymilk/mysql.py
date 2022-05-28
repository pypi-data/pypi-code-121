'''
mysql ORM
基于 pymysql 开发
'''

from re import sub
from math import ceil, floor
from collections import deque
from copy import deepcopy
from pymysql.cursors import DictCursor
from decimal import Decimal
from .toolkit.data_structures import NeedNotExecute, SetAttrError, ParamError
from .toolkit.data_structures import undefined, int0, pinf, uniset, empset
from .localtool import json_chinese as jdumps
from .localtool import quick_iter


class ColumnsError(BaseException): ...
class SliceError(BaseException): ...

class _Factory:

    ''' 不可变类型, 创建后不允许修改. '''

    def __init__(self, where=uniset):
        if where is not empset:
            where = where or uniset
        object.__setattr__(self, 'where', where)

    def __setattr__(self, key, value): raise SetAttrError('_Factory是不可变对象')
    def __bool__(self): return True

    def __and__(self, obj):
        a = self.where
        b = obj.where
        if a is uniset: return _Factory(b)
        if b is uniset: return _Factory(a)
        if a and b: return _Factory(f"({a}) and ({b})")
        return _Factory(empset)

    def __or__(self, obj):
        a = self.where
        b = obj.where
        if a is empset: return _Factory(b)
        if b is empset: return _Factory(a)
        if a is uniset or b is uniset: return _Factory(uniset)
        return _Factory(f"({a}) or ({b})")

    def __invert__(self):
        w = self.where
        if w is uniset: return _Factory(empset)
        if w is empset: return _Factory(uniset)
        return _Factory(f"not ({w})")

    def __sub__(self, obj): return self.__and__(~ obj)
    
    def __str__(self):
        w = self.where
        if w is uniset: return ''
        if w is empset: return ' where 1 = 2'
        return f" where {w}"

class _Filter():

    def __init__(self, field):
        object.__setattr__(self, 'field', field)

    def __setattr__(self, key, value): raise SetAttrError('_Filter是不可变对象')

    def __getattr__(self, name):
        obj = sub('_+$', '', name)
        rlsize = len(name) - len(obj)
        if rlsize == 1:
            return _Filter(field=f"{obj}({self.field})")

    def __eq__(self, obj):
        if obj is None:
            return _Factory(f"{self.field} is null")
        return _Factory(f"{self.field} = {jdumps(obj)}")

    def __ne__(self, obj):
        if obj is None:
            return _Factory(f"{self.field} is not null")
        return _Factory(f"{self.field} != {jdumps(obj)}")

    def __lt__(self, obj): return _Factory(f"{self.field} < {jdumps(obj)}")
    def __le__(self, obj): return _Factory(f"{self.field} <= {jdumps(obj)}")
    def __gt__(self, obj): return _Factory(f"{self.field} > {jdumps(obj)}")
    def __ge__(self, obj): return _Factory(f"{self.field} >= {jdumps(obj)}")
    def re(self, string): return _Factory(f"{self.field} regexp {jdumps(string or '')}")

    def isin(self, *lis):
        if not lis: return _Factory(empset)
        if len(lis) == 1: return self.__eq__(lis[0])
        null = False
        type_item = {str:set(), int:set(), float:set()}
        for i, x, typ in quick_iter(lis):
            if x is None:
                null = True
            else:
                type_item[typ].add(x)
        sumlis = []
        for lis in type_item.values():
            if len(lis) == 1:
                sumlis.append(f"{self.field} = {jdumps(list(lis)[0])}")
            elif len(lis) > 1:
                sumlis.append(f"{self.field} in ({', '.join(jdumps(x) for x in lis)})")
        if null:
            sumlis.append(f"{self.field} is null")
        if len(sumlis) == 1:
            return _Factory(sumlis[0])
        else:
            return _Factory(' or '.join(f"({x})" for x in sumlis))

    def notin(self, *lis):
        if not lis: return _Factory(uniset)
        if len(lis) == 1: return self.__ne__(lis[0])
        null = False
        type_item = {str:set(), int:set(), float:set()}
        for i, x, typ in quick_iter(lis):
            if x is None:
                null = True
            else:
                type_item[typ].add(x)
        sumlis = []
        for lis in type_item.values():
            if len(lis) == 1:
                sumlis.append(f"{self.field} != {jdumps(list(lis)[0])}")
            elif len(lis) > 1:
                sumlis.append(f"{self.field} not in ({', '.join(jdumps(x) for x in lis)})")
        if null:
            sumlis.append(f"{self.field} is not null")
            sumlis = sumlis[0] if len(sumlis) == 1 else ' and '.join(f"({x})" for x in sumlis)
        else:
            sumlis = sumlis[0] if len(sumlis) == 1 else ' and '.join(f"({x})" for x in sumlis)
            sumlis = f"({sumlis}) or ({self.field} is null)"
        return _Factory(sumlis)

class _MakeSlice():
    def __init__(self, func, **param):
        self.func = func
        self.param = param
    def __getitem__(self, key): return self.func(key, **self.param)

class _msheet():

    def __init__(self, mkconn, connpool, sheet, where=None, columns='*', _sort=None):
        if not columns: ParamError('columns 不能为空')
        setv = object.__setattr__
        setv(self, 'mkconn', mkconn)  # lambda : pymysql.connect(**address)
        setv(self, 'connpool', connpool)
        setv(self, 'sheet', sheet)
        setv(self, 'where', where or _Factory(uniset))
        setv(self, 'columns', columns)  # str型 或 tuple型
        setv(self, '_sort', deepcopy(_sort or {}))  # {A:True, B:False, ...}

    def __setattr__(self, key, value): raise SetAttrError('_msheet是不可变对象')
        
    def _deepcopy(self): ...
    def _copy(self, where=undefined, columns=undefined, _sort=undefined):
        return _msheet(
            mkconn = self.mkconn,
            connpool = self.connpool,  # 避免每个过滤器都与MySQL建立新的连接, 造成性能浪费
            sheet = self.sheet,
            where = self.where if where is undefined else where,
            columns = self.columns if columns is undefined else columns,
            _sort = self._sort if _sort is undefined else _sort
        )

    def get_conn(self):
        try:
            conn = self.connpool.popleft()  # 右进左出
            conn.ping(reconnect=True)
            conn.commit()  # pymysql只有在commit的时刻才会获取数据库的最新状态
        except:
            conn = self.mkconn()
        cursor = conn.cursor(cursor=DictCursor)
        return conn, cursor, self.sheet
    
    def _order_sql(self):
        if self._sort:
            return ' order by ' + ', '.join([k if v else f"{k} desc" for k,v in self._sort.items()])
        return ''

    def _columns_sql(self):
        if type(self.columns) is str:
            return self.columns
        return ', '.join(self.columns)
    
    def order(self, **rule): return self._copy(_sort={**self._sort, **rule})  # 必须self._sort在前
    def reset_order(self, **rule): return self._copy(_sort=rule)

    def __add__(self, data):
        conn, cursor, sheet = self.get_conn()
        if type(data) is dict:
            cols = data.keys()
            sql = f"insert into {sheet}({', '.join(cols)}) VALUES ({', '.join(('%s',)*len(cols))})"
            try:
                cursor.execute(sql, tuple(data.values()))
                conn.commit()
                cursor.close()
                self.connpool.append(conn)
                return cursor  # cursor.rowcount, cursor.lastrowid
            except Exception as err:
                conn.rollback()
                raise err
        else:
            cols = set()
            for x in data: cols |= set(x)
            cols = list(cols)
            sql = f"insert into {sheet}({', '.join(cols)}) VALUES ({', '.join(('%s',)*len(cols))})"
            datas = tuple(tuple(x.get(k) for k in cols) for x in data)
            try:
                cursor.executemany(sql, datas)
                conn.commit()
                cursor.close()
                self.connpool.append(conn)
                return cursor
            except Exception as err:
                conn.rollback()
                raise err

    def delete(self, **param): return _MakeSlice(self._ExeDelete, **param)
    def _ExeDelete(self, key, force_size=False, **param):
        size, limit, type_data = self._RStyleSlice(key, action='delete')
        if size or force_size:
            conn, cursor, sheet = self.get_conn()
            try:
                sql = f"delete from {sheet}{self.where}{limit}"
                cursor.execute(sql)
                conn.commit()
                cursor.close()
                self.connpool.append(conn)
                return cursor
            except Exception as err:
                conn.rollback()
                raise err
        else:
            return NeedNotExecute('切片长度为零')

    def update(self, data, **param): return _MakeSlice(self._ExeUpdate, data=data, **param)
    def _ExeUpdate(self, key, data, add_null=False, force_size=False, force_data=False, **param):
        size, limit, type_data = self._RStyleSlice(key, action='update')
        if size or force_size:
            columns = self.columns
            typec = type(columns)
            if columns == '*':
                pass
            elif typec is tuple:
                data = {k:v for k,v in data.items() if k in columns}
            elif columns in data:
                data = {columns: data[columns]}
            else:
                data = {}
            if add_null:
                if columns == '*':
                    raise ColumnsError('add_null=True 时必须指定字段')
                elif typec is tuple:
                    data = {k: data.get(k) for k in columns}
                else:
                    data = {columns: data.get(columns)}
            if data or force_data:
                conn, cursor, sheet = self.get_conn()
                data = ', '.join([f"{k}={jdumps(v)}" for k,v in data.items()])
                try:
                    sql = f"update {sheet} set {data}{self.where}{limit}"
                    cursor.execute(sql)
                    conn.commit()
                    cursor.close()
                    self.connpool.append(conn)
                    return cursor
                except Exception as err:
                    conn.rollback()
                    raise err
            else:
                return NeedNotExecute('没有需要更新的字段')
        else:
            return NeedNotExecute('切片长度为零')

    def exesql(self, sql):
        conn, cursor, sheet = self.get_conn()
        try:
            cursor.execute(sql.replace('{{sheet}}', sheet))
            r = list(cursor.fetchall())
            conn.commit()
            cursor.close()
            self.connpool.append(conn)
            return r
        except Exception as err:
            conn.rollback()
            raise err
    
    def _RStyleSlice(self, key, action='select'):
        '''
        采用R语言的切片风格:
            索引从1开始, 1表示第1个元素, -1表示倒数第1个元素
            切片为双闭区间.
        在此ORM中:
            索引应该 >=1 或 <=-1
            若索引==0则视为1的左边1位
        '''
        total = None
        if type(key) is slice:
            type_data = list
            A = key.start or 1
            if A < 0:
                if total is None: total = self.len()
                A = total + A + 1
            A = ceil(max(1, A))
            B = key.stop
            if B is None or B == -1:
                size = pinf
            elif B == 0:
                size = int0
            else:
                if B < 0:
                    if total is None: total = self.len()
                    B = total + B + 1
                size = max(0, floor(B) - A + 1) or int0
            A -= 1  # 传递给mysql
        else:
            type_data = dict
            size = 1  # 取值的size是1, 勿改成0
            A = int(key)
            if A < 0:
                if total is None: total = self.len()
                A = total + A + 1
            A -= 1  # 传递给mysql
            if A < 0:
                A = pinf
        if action == 'select':
            if A is pinf or size is int0:
                limit = " limit 0"
            elif size is pinf:
                limit = f" limit {A}, 9999999999999" if A else ''
            else:
                limit = f" limit {A}, {size}"
        else:  # update、delete
            if A is pinf or size is int0:
                limit = " limit 0"
            elif A:
                raise SliceError(f"'{action}' 方法的切片不支持跳过首行")
            elif size is pinf:
                limit = ""
            else:
                limit = f" limit {size}"
        return size, limit, type_data

    def get_all_columns(self, comment=False, type=False):
        need = ['column_name as name']
        if comment: need.append('column_comment as comment')
        if type: need.append('column_type as type')
        need = ', '.join(need)
        conn, cursor, sheet = self.get_conn()
        db = conn.db.decode()
        sql = f"select {need} from information_schema.columns where table_schema = '{db}' and table_name = '{sheet}'"
        cursor.execute(sql)
        res = list(cursor.fetchall())
        cursor.close()
        return res
    
    def len(self):
        conn, cursor, sheet = self.get_conn()
        cursor.execute(f"select count(1) as tatal from {sheet}{self.where}")
        tatal = list(cursor.fetchall())[0]['tatal']
        cursor.close()
        self.connpool.append(conn)
        return tatal
    __len__ = len

    def __getitem__(self, key):
        type_ = type(key)
        # 查询
        if type_ in (slice, int, float, Decimal):
            size, limit, type_data = self._RStyleSlice(key)
            if not size: return []  # 此时 type_data 必然是list
            conn, cursor, sheet = self.get_conn()
            sql = f"select {self._columns_sql()} from {sheet}{self.where}{self._order_sql()}{limit}"
            cursor.execute(sql)
            lines = list(cursor.fetchall())
            cursor.close()
            self.connpool.append(conn)
            return lines if type_data is list else lines[0]
        # 限定columns
        elif type_ in (str, tuple):  # 输入多个字符串, 用逗号隔开, Python会自动打包成tuple
            return self._copy(columns=key)
        # _Factory
        elif type_ is _Factory:
            return self._copy(where=self.where & key)

class mysqldb():

    def __init__(self, mkconn, maxsize=None):
        self.maxsize = maxsize
        self.mkconn = mkconn
        self.connpool = deque([mkconn()], maxlen=maxsize)

    def __getitem__(self, sheet):
        return _msheet(
            mkconn = self.mkconn,
            connpool = self.connpool,
            sheet = sheet
        )

    def mksheet(self, sheet):
        return _msheet(
            mkconn = self.mkconn,
            connpool = deque([self.mkconn()], maxlen=self.maxsize),
            sheet = sheet
        )

class _MysqlColumn():
    def __getattr__(self, field): return _Filter(field=field)

mc = _MysqlColumn()
