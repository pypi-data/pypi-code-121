import configparser


class Config:
    def __init__(self, cfg_file_path):
        self.config: configparser.ConfigParser = self.base_config(cfg_file_path)

    @staticmethod
    def base_config(cfg_file_path=None):
        config = configparser.ConfigParser()
        config.read(cfg_file_path, encoding="utf-8")
        return config

    def mongo(self):
        return dict(self.config.items('mongo'))

    def redis(self):
        return dict(self.config.items('redis'))

    def rabbitmq(self):
        return dict(self.config.items('rabbitmq'))

    def client(self):
        return dict(self.config.items('client'))

    def oss(self):
        return dict(self.config.items('oss'))

    def other(self):
        return dict(self.config.items('other'))

    # @staticmethod
    # def explain(func_text):
    #     """
    #     :param func_text: 函数的字符串形式，函数名必须为parse_func
    #     :return:
    #     """
    #     exec(func_text, globals())
    #     parse_func = eval('parse_func')
    #     return parse_func
