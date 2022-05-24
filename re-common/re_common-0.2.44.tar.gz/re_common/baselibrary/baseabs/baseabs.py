

class BaseAbs(object):
    """
    抽象工厂模式，方便管理和引用 目前主要将配置文件和sql相关的库引入了抽象工厂模式中
    """
    @staticmethod
    def get_sql_factory():
        """
        sql相关的工厂
        :return:
        """
        from re_common.baselibrary.database.sql_factory import SqlFactory
        return SqlFactory()

    @staticmethod
    def get_config_factory():
        """
        配置文件相关的工厂
        :return:
        """
        from re_common.baselibrary.readconfig.config_factory import ConfigFactory
        return ConfigFactory()



