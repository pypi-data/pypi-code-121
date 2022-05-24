import aiomysql

from re_common.baselibrary import IniConfig
from re_common.baselibrary.readconfig.toml_config import TomlConfig


class BaseAioMysql(object):

    def __init__(self):
        self.conn: aiomysql.connection.Connection

    def set_conn_dicts(self, dicts):
        self.host = dicts["host"]
        self.port = dicts["port"]
        self.user = dicts["user"]
        self.password = dicts["password"]
        self.db = dicts["db"]
        self.loop = dicts["loop"]
        return self

    def set_conn_ini(self, config_ini, secs='mysql'):
        """
        使用配置文件连接
        :param config_ini:
        :return:
        """
        dicts = IniConfig(config_ini).builder().get_config_dict()
        self.set_conn_dicts(dicts[secs])
        return self

    def set_conn_toml(self, config_toml, secs=None):
        """
        使用配置文件连接
        :param config_ini:
        :return:
        """
        dicts = TomlConfig(config_toml).get_config_dicts()
        if secs:
            dicts = dicts[secs]
        self.set_conn_dicts(dicts)
        return self

    def set_loop(self, loop):
        self.loop = loop
        return self

    async def conn_mysql(self):
        self.conn = await aiomysql.connect(
            host=self.host, port=self.port,
            user=self.user, password=self.password,
            db=self.db, loop=self.loop)
        return self

    async def exec_sql(self, sql, args=None):
        await self.conn_mysql()
        cur = await self.conn.cursor()
        # count 已生成的受影响的行数
        count = await cur.execute(sql, args)
        # https://aiomysql.readthedocs.io/en/latest/cursors.html?highlight=description#Cursor.description
        # 此只读属性是7个项目的序列的序列。
        # print(cur.description)
        # 返回的查询值
        r = await cur.fetchall()
        await cur.close()
        return r

    async def get_pool(self):
        self.pool = await aiomysql.create_pool(
            host=self.host, port=self.port,
            user=self.user, password=self.password,
            db=self.db, loop=self.loop,
            autocommit=False)

    async def pool_exec(self, sql, arg=None):
        await self.get_pool()
        with (await self.pool) as conn:
            cur = await conn.cursor()
            await cur.execute(sql, arg)
            (r,) = await cur.fetchone()
        return r

    def close_conn(self):
        self.conn.close()

    async def close_pool(self):
        await self.pool.wait_closed()
        self.pool.close()
