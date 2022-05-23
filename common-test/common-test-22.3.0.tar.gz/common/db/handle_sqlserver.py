import pymssql
import sysconfig
import yaml
import os

# class sqlerverDB:
        # def __init__(self, config):
        #     """初始化连接sqlerver"""
        #     self.conn = pymssql.connect(
        #         host=config.get("host"),
        #         port=config.get("port"),
        #         user=config.get("user"),
        #         password=config.get("password"),
        #         db=config.get("db_name"),
        #         charset='utf8mb4',
        #         cursorclass=pymssql.cursors.DictCursor
        #     )


class YamlHandler:
    def __init__(self, file):
        self.file = file

    def read_yaml(self, encoding='utf-8'):
        """读取yaml数据"""
        with open(self.file, encoding=encoding) as f:
            return yaml.load(f.read(), Loader=yaml.FullLoader)

    def write_yaml(self, data, encoding='utf-8'):
        """向yaml文件写入数据"""
        with open(self.file, encoding=encoding, mode='w') as f:
            return yaml.dump(data, stream=f, allow_unicode=True)


if __name__ == '__main__':
    # 读取config.yaml配置文件数据
    read_data = YamlHandler('../config/config.yaml').read_yaml()
    # 将data数据写入config1.yaml配置文件
    # write_data = YamlHandler('../config/config1.yaml').write_yaml(data)
    print(read_data)


