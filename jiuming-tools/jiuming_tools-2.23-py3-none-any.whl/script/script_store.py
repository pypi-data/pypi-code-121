
class ScriptConfig(object):
    """
    脚本配置 对象
    """
    # 脚本类型  如 sh  bash  python   以linux shell的脚本引擎名称   执行脚本的时候  就是 type ./xxx
    type: str
    # 脚本名称
    name: str
    # 脚本备注
    remark: str
    # 脚本地址
    path: str

    def __init__(self, type, name, remark, path):
        self.type = type
        self.name = name
        self.remark = remark
        self.path = path

    @staticmethod
    def to_obj(d: dict):
        """
        将读取的dict 转换为 serverConfig
        :param d:  dict
        :return: ServerConfig
        """
        return ScriptConfig(type=d['type'], name=d['name'],
                            remark=d['remark'], path=d['path'])
