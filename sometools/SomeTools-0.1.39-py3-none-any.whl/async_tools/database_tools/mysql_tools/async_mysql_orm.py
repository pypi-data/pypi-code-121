import asyncio
import aiomysql
import platform
from datetime import datetime

if not (platform.system() == 'Windows'):
    import uvloop

    asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())  # 使用 uvloop 来替换 asyncio 内部的事件循环。


class AsyncMysqlOrmMixIn:
    def __init__(self, *args, **kwargs):
        super(AsyncMysqlOrmMixIn, self).__init__(*args, **kwargs)

    async def create_db_conn_pool(self, **kwargs):
        print(f'create_database_connection_pool:{kwargs.get("DATABASE_HOST")}')
        return await aiomysql.create_pool(
            host=kwargs.get("DATABASE_HOST"),
            port=kwargs.get("DATABASE_PORT"),
            user=kwargs.get("DATABASE_USER"),
            password=kwargs.get("DATABASE_PWD"),
            db=kwargs.get("DATABASE_DB"),
            charset=kwargs.get("DATABASE_CHARSET"),
            autocommit=kwargs.get("DATABASE_AUTOCOMMIT"),
            maxsize=kwargs.get("DATABASE_MAX"),
            minsize=kwargs.get("DATABASE_MIN"),
            loop=asyncio.get_running_loop()
        )


async def _exec_select_sql(db_pool, sql, args, size=None):
    async with db_pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            # try:
            await cur.execute(sql.replace('?', '%s'), args or ())
            # print(cur.description)
            if size:
                rs = await cur.fetchmany(size)
            else:
                rs = await cur.fetchall()
                # (r,) = await cur.fetchone()
            await cur.close()
            # print('rows returned: %s' % len(rs))
            return rs
            # finally:
            #     if cur:
            #         await cur.close()
            #     # 释放掉conn,将连接放回到连接池中
            #     await db_pool.release(conn)
            #


async def _execute(db_pool, sql, args, autocommit=True):
    async with db_pool.acquire() as conn:
        if not autocommit:
            await conn.begin()
        async with conn.cursor(aiomysql.DictCursor) as cur:
            try:
                await cur.execute(sql.replace('?', '%s'), args)
                last_id = cur.lastrowid
                affected = cur.rowcount
                await cur.close()
                if not autocommit:
                    await conn.commit()
            except BaseException as e:
                _last_executed = cur._last_executed
                if not autocommit:
                    await conn.rollback()
                raise Exception(f"{e.__class__.__name__}\nlast_executed_sql:\n{_last_executed}\n error_content:\n{e}")
            return last_id, affected


def _create_args_string(num):
    L = []
    for n in range(num):
        L.append('?')
    return ', '.join(L)


class Field(object):

    def __init__(self, name, column_type, primary_key, default):
        self.name = name
        self.column_type = column_type
        self.primary_key = primary_key
        self.default = default

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.name)


class StringField(Field):

    def __init__(self, name=None, primary_key=False, default=None, ddl='varchar(100)'):
        super().__init__(name, ddl, primary_key, default)


class BooleanField(Field):

    def __init__(self, name=None, default=False):
        super().__init__(name, 'boolean', False, default)


class IntegerField(Field):

    def __init__(self, name=None, primary_key=False, default=0):
        super().__init__(name, 'bigint', primary_key, default)


class FloatField(Field):

    def __init__(self, name=None, primary_key=False, default=0.0):
        super().__init__(name, 'real', primary_key, default)


class TextField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'text', False, default)


class DateTimeField(Field):

    def __init__(self, name=None, default=None):
        super().__init__(name, 'datetime', False, default)


class ModelMetaclass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)
        tableName = attrs.get('__table__', None) or name
        cls.__table__ = tableName
        # print('found model: %s (table: %s)' % (name, tableName))
        mappings = dict()
        fields = []
        primaryKey = None
        for k, v in attrs.items():
            if isinstance(v, Field):
                # print('  found mapping: %s ==> %s' % (k, v))
                mappings[k] = v
                if v.primary_key:
                    # 找到主键:
                    if primaryKey:
                        raise Exception('Duplicate primary key for field: %s' % k)
                    primaryKey = k
                else:
                    fields.append(k)
        if not primaryKey:
            raise Exception('Primary key not found.')
        for k in mappings.keys():
            attrs.pop(k)
        escaped_fields = list(map(lambda f: '`%s`' % f, fields))
        attrs['__mappings__'] = mappings  # 保存属性和列的映射关系
        attrs['__table__'] = tableName
        attrs['__primary_key__'] = primaryKey  # 主键属性名
        attrs['__fields__'] = fields  # 除主键外的属性名
        attrs['__select__'] = 'select `%s`, %s from `%s`' % (
            primaryKey, ', '.join(escaped_fields), "__Placeholder_identifier__")
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (
            "__Placeholder_identifier__", ', '.join(escaped_fields), primaryKey,
            _create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (
            "__Placeholder_identifier__", ', '.join(map(lambda f: '`%s`=?' % (mappings.get(f).name or f), fields)),
            primaryKey)
        attrs['__delete__'] = 'delete from `%s` where `%s`=?' % ("__Placeholder_identifier__", primaryKey)
        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaclass):

    def __init__(self, **kw):
        super(Model, self).__init__(**kw)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return getattr(self, key, None)

    def getValueOrDefault(self, key):
        value = getattr(self, key, None)
        field = self.__mappings__[key]
        if value is None:
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                setattr(self, key, value)
        else:
            if platform.system() == 'Windows':
                if isinstance(field, StringField):
                    if not (isinstance(value, str) or isinstance(value, bytes)):
                        raise TypeError(
                            f'表:{self.__table__}--字段:{key}--值:{value}==现类型:{type(value).__name__}与定义类型str不符')
                if isinstance(field, BooleanField):
                    if not (isinstance(value, bool) or isinstance(value, int)):
                        raise TypeError(
                            f'表:{self.__table__}--字段:{key}--值:{value}==现类型:{type(value).__name__}与定义类型bool、int不符')
                if isinstance(field, IntegerField):
                    if not isinstance(value, int):
                        raise TypeError(
                            f'表:{self.__table__}--字段:{key}--值:{value}==现类型:{type(value).__name__}与定义类型int不符')
                if isinstance(field, FloatField):
                    if not isinstance(value, float):
                        raise TypeError(
                            f'表:{self.__table__}--字段:{key}--值:{value}==现类型:{type(value).__name__}与定义类型float不符')
                if isinstance(field, TextField):
                    if not (isinstance(value, str) or isinstance(value, bytes)):
                        raise TypeError(
                            f'表:{self.__table__}--字段:{key}--值:{value}==现类型:{type(value).__name__}与定义类型str不符')
                if isinstance(field, DateTimeField):
                    if not (isinstance(value, datetime) or isinstance(value, str)):
                        raise TypeError(
                            f'表:{self.__table__}--字段:{key}--值:{value}==现类型:{type(value).__name__}与定义类型datetime不符')
        return value

    @classmethod
    async def execute_sql(cls, sql_statement=None):
        async with cls.__db_conn_pool__.acquire() as conn:
            async with conn.cursor(aiomysql.DictCursor) as cur:
                await cur.execute(sql_statement)
                rs = await cur.fetchall()
                await cur.close()
                return rs

    @classmethod
    async def select_by_where(cls, db_pool=None, table_name=None, **kwargs) -> list:
        """
        where条件查询,适用于固定相等的筛选条件
        """
        if not table_name:
            table_name = cls.__table__
        if not db_pool:
            db_pool = cls.__db_conn_pool__
        sql = [cls.__select__.replace("__Placeholder_identifier__", table_name)]
        _temp_list = []
        index = 0
        for key, value in kwargs.items():
            index += 1
            if key not in ['order_by', 'limit']:
                if index == 1:
                    sql.append('where')
                if index > 1:
                    sql.append('and')
                sql.append(f'{key}=?')
                _temp_list.append(value)
            else:
                if key == 'order_by':
                    sql.append(f'order by {value}')
                    # _temp_list.remove(value)
                if key == 'limit':
                    sql.append('limit')
                    if isinstance(value, int):
                        sql.append('?')
                        _temp_list.append(value)
                    elif isinstance(value, tuple) and len(value) == 2:
                        sql.append('?, ?')
                        _temp_list.extend(value)
                    else:
                        raise ValueError('Invalid limit value: %s' % str(value))
        rs = await _exec_select_sql(db_pool, ' '.join(sql), _temp_list)
        return [cls(**r) for r in rs]

    async def save_db_date(self, table_name=None) -> int:
        if not table_name:
            table_name = self.__table__
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        temp_list = []
        for i in args:
            if i == []:
                temp_list.append(None)
            else:
                temp_list.append(i)
        data_pk, rows = await _execute(self.__db_conn_pool__,
                                       self.__insert__.replace("__Placeholder_identifier__", table_name),
                                       temp_list)
        if rows != 1:
            raise BaseException('failed to insert record: affected rows: %s' % rows)
        return data_pk

    async def update_db_date(self, table_name=None):
        if not table_name:
            table_name = self.__table__
        args = list(map(self.getValue, self.__fields__))
        args.append(self.getValue(self.__primary_key__))
        data_pk, rows = await _execute(self.__db_conn_pool__,
                                       self.__update__.replace("__Placeholder_identifier__", table_name),
                                       args)
        if rows != 1:
            print('failed to update by primary key: affected rows: %s' % rows)
        return rows

    async def remove_db_date(self, table_name=None):
        if not table_name:
            table_name = self.__table__
        args = [self.getValue(self.__primary_key__)]
        data_pk, rows = await _execute(self.__db_conn_pool__, self.__delete__.replace("__Placeholder_identifier__", table_name), args)
        if rows != 1:
            raise BaseException('failed to remove by primary key: affected rows: %s' % rows)
        return rows

    @classmethod
    async def create_db_table(cls, db_pool, sql, autocommit=True):
        async with cls.__db_conn_pool__.acquire() as conn:
            if not autocommit:
                await conn.begin()
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(sql)
                    affected = cur.rowcount
                    await cur.close()
                    if not autocommit:
                        await conn.commit()
                except BaseException as e:
                    if not autocommit:
                        await conn.rollback()
                    raise e
                return affected

    @classmethod
    async def table_exists(cls, table_name=None, autocommit=True):
        if not table_name:
            table_name = cls.__table__
        sql = f"SHOW TABLES like '{table_name}';"
        async with cls.__db_conn_pool__.acquire() as conn:
            if not autocommit:
                await conn.begin()
            async with conn.cursor(aiomysql.DictCursor) as cur:
                try:
                    await cur.execute(sql)
                    affected = cur.rowcount
                    await cur.close()
                    if not autocommit:
                        await conn.commit()
                except BaseException as e:
                    if not autocommit:
                        await conn.rollback()
                    raise e
                return affected
