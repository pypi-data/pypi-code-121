import sys
import traceback

import pymysql

from re_common.baselibrary import MLogger
from re_common.baselibrary.baseabs import BaseAbs
from re_common.baselibrary.database.mbuilder import MysqlBuilderAbstract
from re_common.baselibrary.database.moudle import SqlMoudle
from re_common.baselibrary.readconfig.ini_config import IniConfig
from re_common.baselibrary.readconfig.toml_config import TomlConfig


class MysqlBuilder(MysqlBuilderAbstract):
    def __init__(self, configfile, configname, keytransformdicts=None):
        # sql的moudle对象 mysql通过该对象对接参数
        self.sqlmoudle = SqlMoudle()
        # 获取配置文件对象
        self.ic = IniConfig(configfile).builder()
        # 配置文件位置
        self.configfile = configfile
        # 配置文件的sections
        self.configname = configname
        # 使用key转换器转换key(主要用于配置文件的key与我们默认读取时的key不一致)
        self.keytransformdicts = keytransformdicts
        """
        python2
            self.config.readfp(open(configfile, 'rb'))
        python3
            self.config.read_file(open(configfile, 'r'))
        """

    def build_port(self, port):
        self.sqlmoudle.port = int(self.ic.get_value(self.configname, port))
        return self

    def build_server_address(self, host):
        self.sqlmoudle.host = self.ic.get_value(self.configname, host)
        return self

    def build_password(self, passwd):
        self.sqlmoudle.passwd = self.ic.get_value(self.configname, passwd)
        return self

    def use_db(self, db):
        self.sqlmoudle.db = self.ic.get_value(self.configname, db)
        return self

    def build_username(self, user):
        self.sqlmoudle.user = self.ic.get_value(self.configname, user)
        return self

    def build_chart(self, chartset):
        self.sqlmoudle.charset = self.ic.get_value(self.configname, chartset)
        return self

    def build_cursorclass(self, cursornum):
        if cursornum == 1:
            self.sqlmoudle.cursorclass = pymysql.cursors.DictCursor
        else:
            # 默认保持不变
            pass

        return self

    # def build_cursorclass(self,cursorclass):
    #     self.sqlmoudle.cursorclass = self.ic.get_value(self.configname, cursorclass)

    def get_moudle(self):
        """
        返回数据库连接需要的对象
        :return:
        """
        return self.sqlmoudle

    def build_all(self):
        if not self.keytransformdicts:
            # 不传入时不转换
            self.keytransformdicts = {"port": "port", "host": "host", "passwd": "passwd", "user": "user", "db": "db",
                                      "chartset": "chartset"}
        self.build_port(self.keytransformdicts["port"])
        self.build_server_address(self.keytransformdicts["host"])
        self.build_password(self.keytransformdicts["passwd"])
        self.build_username(self.keytransformdicts["user"])
        self.use_db(self.keytransformdicts["db"])
        self.build_chart(self.keytransformdicts["chartset"])
        return self

    def get_tuples(self):
        return self.sqlmoudle.host, self.sqlmoudle.user, self.sqlmoudle.passwd, self.sqlmoudle.port


class MysqlBuilderForToml(MysqlBuilderAbstract):
    def __init__(self, configfile, sesc, keytransformdicts=None):
        # sql的moudle对象 mysql通过该对象对接参数
        self.sqlmoudle = SqlMoudle()
        # 获取配置文件对象
        self.dic = TomlConfig(configfile).read_file_remove_bom().get_dicts()
        # 配置文件位置
        self.configfile = configfile
        # 配置文件的sections
        self.sesc = sesc
        # 使用key转换器转换key(主要用于配置文件的key与我们默认读取时的key不一致)
        self.keytransformdicts = keytransformdicts
        """
        python2
            self.config.readfp(open(configfile, 'rb'))
        python3
            self.config.read_file(open(configfile, 'r'))
        """

    def build_port(self, port):
        self.sqlmoudle.port = int(self.dic[self.sesc][port])
        return self

    def build_server_address(self, host):
        self.sqlmoudle.host = self.dic[self.sesc][host]
        return self

    def build_password(self, passwd):
        self.sqlmoudle.passwd = self.dic[self.sesc][passwd]
        return self

    def use_db(self, db):
        self.sqlmoudle.db = self.dic[self.sesc][db]
        return self

    def build_username(self, user):
        self.sqlmoudle.user = self.dic[self.sesc][user]
        return self

    def build_chart(self, chartset):
        self.sqlmoudle.charset = self.dic[self.sesc][chartset]
        return self

    def build_cursorclass(self, cursornum):
        if cursornum == 1:
            self.sqlmoudle.cursorclass = pymysql.cursors.DictCursor
        else:
            # 默认保持不变
            pass

        return self

    def get_moudle(self):
        """
        返回数据库连接需要的对象
        :return:
        """
        return self.sqlmoudle

    def build_all(self):
        if not self.keytransformdicts:
            # 不传入时不转换
            self.keytransformdicts = {"port": "port", "host": "host", "passwd": "passwd", "user": "user", "db": "db",
                                      "chartset": "chartset"}
        self.build_port(self.keytransformdicts["port"])
        self.build_server_address(self.keytransformdicts["host"])
        self.build_password(self.keytransformdicts["passwd"])
        self.build_username(self.keytransformdicts["user"])
        self.use_db(self.keytransformdicts["db"])
        self.build_chart(self.keytransformdicts["chartset"])
        return self

    def get_tuples(self):
        return self.sqlmoudle.host, self.sqlmoudle.user, self.sqlmoudle.passwd, self.sqlmoudle.port


class MysqlBuilderForDicts(MysqlBuilderAbstract):
    def __init__(self, dicts, keytransformdicts=None):
        # sql的moudle对象 mysql通过该对象对接参数
        self.sqlmoudle = SqlMoudle()
        self.dicts = dicts
        # 使用key转换器转换key(主要用于配置文件的key与我们默认读取时的key不一致)
        self.keytransformdicts = keytransformdicts

    def build_port(self, port):
        self.sqlmoudle.port = int(self.dicts[port])
        return self

    def build_server_address(self, host):
        self.sqlmoudle.host = self.dicts[host]
        return self

    def build_password(self, passwd):
        self.sqlmoudle.passwd = self.dicts[passwd]
        return self

    def use_db(self, db):
        self.sqlmoudle.db = self.dicts[db]
        return self

    def build_username(self, user):
        self.sqlmoudle.user = self.dicts[user]
        return self

    def build_chart(self, chartset):
        self.sqlmoudle.charset = self.dicts[chartset]
        return self

    def build_cursorclass(self, cursornum):
        if cursornum == 1:
            self.sqlmoudle.cursorclass = pymysql.cursors.DictCursor
        else:
            # 默认保持不变
            pass

        return self

    def get_moudle(self):
        """
        返回数据库连接需要的对象
        :return:
        """
        return self.sqlmoudle

    def build_all(self):
        if not self.keytransformdicts:
            # 不传入时不转换
            self.keytransformdicts = {"port": "port", "host": "host", "passwd": "passwd", "user": "user", "db": "db",
                                      "chartset": "chartset"}
        self.build_port(self.keytransformdicts["port"])
        self.build_server_address(self.keytransformdicts["host"])
        self.build_password(self.keytransformdicts["passwd"])
        self.build_username(self.keytransformdicts["user"])
        self.use_db(self.keytransformdicts["db"])
        self.build_chart(self.keytransformdicts["chartset"])
        return self

    def get_tuples(self):
        return self.sqlmoudle.host, self.sqlmoudle.user, self.sqlmoudle.passwd, self.sqlmoudle.port


class MysqlUtiles(object):
    def __init__(self, cfgfilepath, sesc, logger=None, keytransformdicts=None, builder="MysqlBuilder", cursorsnum=0,
                 dicts=None):
        """

        :param cfgfilepath:
        :param sesc:
        :param logger:
        :param keytransformdicts:
        :param builder:
        :param cursors: 0表示默认，1 表示dicts 其他情况后面再添加
        """
        self._logger = logger
        # 通过工厂方法获取mysql对象
        self.mysql = BaseAbs.get_sql_factory().mysql_factory("mysql")
        # mysql 连接通过builder进行适配 这里的builder通过配置文件获取相关连接信息
        # 也可以通过继承 MysqlBuilderAbstract 后自己手动设置builer
        if builder == "MysqlBuilder":
            self.builder = MysqlBuilder(cfgfilepath, sesc, keytransformdicts)
        elif builder == "MysqlBuilderForToml":
            self.builder = MysqlBuilderForToml(cfgfilepath, sesc, keytransformdicts)
        elif builder == "MysqlBuilderForDicts":
            self.builder = MysqlBuilderForDicts(dicts, keytransformdicts)
        else:
            raise Exception("传入builder 参数有误")
        self.builder = self.builder.build_all().build_cursorclass(cursorsnum)
        self.moudle = self.builder.get_moudle()
        # 连接mysql通过唯一适配moudle
        # print(self.moudle.to_dict())
        self.mysql.link(self.moudle)

    @property
    def logger(self):
        if self._logger is None:
            self._logger = MLogger().streamlogger
        return self._logger

    @logger.setter
    def logger(self, value):
        assert isinstance(value, MLogger)
        self._logger = value

    # 更新数据库状态
    def ExeSqlListToDB(self, sSqlList, errExit=True, args=None):
        """
        该函数处理一个sql列表 没有返回并将列表置空
        :param sSqlList:
        :return:
        """
        dbMsg = None
        if not self.mysql:
            raise ValueError("database conn or database config must have to have one")
        if not self.mysql.is_ping():
            self.mysql.reConnect()
        cursor = self.mysql.get_new_cursor()
        errcount = 0
        successcount = 0
        for sql in sSqlList:
            try:
                self.logger.info(sql + ";" + str(args))
                cursor.execute(sql, args=args)
                successcount += 1
            except:
                errcount += 1
                self.mysql.commit()
                self.logger.error('*errSql:' + sql)
                dbMsg = '*updateError:' + traceback.format_exc()
                if errExit:
                    self.logger.error(dbMsg)
                    sys.exit(-1)
            if dbMsg:
                self.logger.error(dbMsg)
        self.mysql.commit()
        cursor.close()
        if errcount:
            return False, successcount, errcount
        else:
            return True, successcount, errcount

    def SelectFromDB(self, sSql, errExit=True, args=None):
        """
        使用sql语句查询并返回结果列表
        :param sql:
        :return:
        """
        if not self.mysql:
            raise ValueError("database conn or database config must have to have one")
        if self.mysql.is_ping():
            self.mysql.reConnect()
        cursor = self.mysql.get_new_cursor()
        try:
            self.logger.info(sSql + ";" + str(args))
            result = cursor.execute(sSql, args=args)
            rows = cursor.fetchall()
            return True, rows
        except:
            self.logger.error('* errSql:' + sSql)
            sMsg = '* errSynax:' + traceback.format_exc()
            if errExit:
                self.logger.error(sMsg)
                sys.exit(-1)
        finally:
            self.mysql.commit()
            cursor.close()
        if sMsg:
            self.logger.error(sMsg)
            return False, sMsg

    def SelectFromDBFetchOne_noyield(self, sSql, errExit=True, args=None):
        """
        使用sql语句查询并返回结果列表
        :param sql:
        :return:
        """
        if not self.mysql:
            raise ValueError("database conn or database config must have to have one")
        if self.mysql.is_ping():
            self.mysql.reConnect()
        cur = self.mysql.get_new_cursor()
        try:
            self.logger.info(sSql + ";" + str(args))
            result = cur.execute(sSql, args=args)
            return True, cur.fetchone()
        except:
            self.logger.error('* errSql:' + sSql)
            sMsg = '* errSynax:' + traceback.format_exc()
            if errExit:
                self.logger.error(sMsg)
                sys.exit(-1)
        finally:
            self.mysql.commit()
            cur.close()
        if sMsg:
            self.logger.error(sMsg)
            return False, sMsg

    def SelectFromDBFetchOne(self, sSql, errExit=True, args=None):
        """
        使用sql语句查询并返回结果列表
        :param sql:
        :return:
        """
        if not self.mysql:
            raise ValueError("database conn or database config must have to have one")
        if self.mysql.is_ping():
            self.mysql.reConnect()
        cur = self.mysql.get_new_cursor()
        try:
            self.logger.info(sSql + ";" + str(args))
            result = cur.execute(sSql, args=args)
            while True:
                row = cur.fetchone()
                if row is None:
                    return None
                else:
                    yield row
        except:
            self.logger.error('* errSql:' + sSql)
            sMsg = '* errSynax:' + traceback.format_exc()
            if errExit:
                self.logger.error(sMsg)
                sys.exit(-1)
        finally:
            self.mysql.commit()
            cur.close()
        if sMsg:
            self.logger.error(sMsg)
            return None

    def ExeSqlToDB(self, sSql, errExit=True, args=None):
        if not self.mysql:
            raise ValueError("database conn or database config must have to have one")
        if self.mysql.is_ping():
            self.mysql.reConnect()
        cur = self.mysql.get_new_cursor()
        try:
            self.logger.info(sSql + ";" + str(args))
            rows = cur.execute(sSql, args=args)
            self.mysql.commit()
            return True, rows
        except:
            self.mysql.rollback()
            sMsg = '* errSynax:' + traceback.format_exc()
            if errExit:
                self.logger.error(sMsg)
                sys.exit(-1)
        finally:
            self.mysql.commit()
            cur.close()
        if sMsg:
            self.logger.error(sMsg)
            return False, sMsg

    # 更新数据库状态
    def ExeSqlMany(self, sSql, args, errExit=True):
        """
        该函数处理一个sql列表 没有返回并将列表置空
        :param conn:
        :param sSqlList:
        :return:
        """

        if not self.mysql:
            raise ValueError("database conn or database config must have to have one")
        if self.mysql.is_ping():
            self.mysql.reConnect()
        cur = self.mysql.get_new_cursor()
        try:
            self.logger.info(sSql + ";" + str(args))
            rows = cur.executemany(sSql, args=args)
            self.mysql.commit()
            return True, rows
        except:
            self.mysql.rollback()
            self.logger.error('*errSql:' + sSql)
            dbMsg = '*updateError:' + traceback.format_exc()
            if errExit:
                self.logger.error(dbMsg)
                sys.exit(-1)
        finally:
            self.mysql.commit()
            cur.close()
        if dbMsg:
            self.logger.error(dbMsg)
            return False, dbMsg

    def escape_string(self, string):
        return self.mysql.escape(string)

    def pymysql_escape_string(self, strings):
        return self.mysql.escape(strings)

    def close(self):
        self.mysql.db.close()
