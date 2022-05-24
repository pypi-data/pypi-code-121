from abc import ABCMeta, abstractmethod

from re_common.baselibrary.database.moudle import SqlMoudle, Sqlite3Moudle


class MysqlBuilderAbstract:
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_server_address(self, host):
        pass

    @abstractmethod
    def build_username(self, user):
        pass

    @abstractmethod
    def build_password(self, passwd):
        pass

    @abstractmethod
    def build_port(self, port):
        pass

    @abstractmethod
    def use_db(self, db):
        pass

    @abstractmethod
    def build_chart(self, chartset):
        pass

    @abstractmethod
    def get_moudle(self):
        pass


class Sqlite3BuilderAbstract:
    __metaclass__ = ABCMeta

    @abstractmethod
    def build_file_path(self, dbpath):
        pass

    @abstractmethod
    def build_isolation_level(self):
        pass


class MysqlBuilder(MysqlBuilderAbstract):
    def __init__(self, configfile, configname, keytransformdicts=None):
        self.sqlmoudle = SqlMoudle()

        from re_common.baselibrary.readconfig.ini_config import IniConfig
        self.ic = IniConfig(configfile).builder()
        self.configfile = configfile
        self.configname = configname
        # 使用key转换器转换key
        self.keytransformdicts = keytransformdicts
        """
        python2
            self.config.readfp(open(configfile, 'rb'))
        python3
            self.config.read_file(open(configfile, 'r'))
        """

    def build_port(self, port):
        self.sqlmoudle.port = int(self.ic.get_value(self.configname, port))

    def build_server_address(self, host):
        self.sqlmoudle.host = self.ic.get_value(self.configname, host)

    def build_password(self, passwd):
        self.sqlmoudle.passwd = self.ic.get_value(self.configname, passwd)

    def use_db(self, db):
        self.sqlmoudle.db = self.ic.get_value(self.configname, db)

    def build_username(self, user):
        self.sqlmoudle.user = self.ic.get_value(self.configname, user)

    def build_chart(self, chartset):
        self.sqlmoudle.charset = self.ic.get_value(self.configname, chartset)

    def get_moudle(self):
        return self.sqlmoudle

    def build_all(self):
        if not self.keytransformdicts:
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


class Sqlite3Builder(Sqlite3BuilderAbstract):
    def __init__(self, configfile="", sec=""):
        self.sqlite3moudle = Sqlite3Moudle()
        from re_common.baselibrary.readconfig.ini_config import IniConfig
        self.ic = IniConfig(configfile).builder()
        self.configfile = configfile
        self.sec = sec

    def build_file_path(self, dbpath='', opt="dbpath"):
        if dbpath:
            self.sqlite3moudle.database = dbpath
        else:
            self.sqlite3moudle.database = self.ic.get_value(self.sec, opt)
        return self

    def build_timeout(self, timeout):
        self.sqlite3moudle.timeout = timeout
        return self

    def build_isolation_level(self):
        pass

    def build_all(self):
        self.build_file_path()
        self.build_isolation_level()
        return self

    def get_moudle(self):
        return self.sqlite3moudle
