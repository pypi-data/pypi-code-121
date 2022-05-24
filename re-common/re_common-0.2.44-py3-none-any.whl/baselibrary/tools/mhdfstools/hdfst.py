from re_common.baselibrary.baseabs import BaseAbs
from re_common.baselibrary.utils.basehdfs import BaseHDFS


class HdfsTools(object):
    def __init__(self):
        self.toml_file = "config_down.toml"
        self.dicts = {}
        self.basehdfs = None

    def read_toml(self):
        dicts = BaseAbs.get_config_factory().toml_factory().set_config_path(
            self.toml_file).read_file_remove_bom().get_dicts()
        self.dicts = dicts
        return self

    def set_basehdfs(self, i=0):
        self.basehdfs = BaseHDFS()
        self.basehdfs.hdfsdir = self.dicts["PathPair"][i][0]
        self.basehdfs.localdir = self.dicts["PathPair"][i][1]
        self.basehdfs.user_name = self.dicts["UserName"]
        self.basehdfs.namenode = self.dicts["NameNode"]
        return self

    def builder(self):
        self.basehdfs.get_client()

    def create_dirs(self):
        self.basehdfs.get_client()
        print(self.basehdfs.mk_hdfs_dirs(r"/RawData/wanfang/qk/ref/big_json/20200421"))


    def exists(self):
        print(self.basehdfs.exists(r"/RawData/wanfang/qk/ref/big_json/20200421"))

    def run(self):
        self.read_toml()
        self.set_basehdfs()
        self.builder()
        self.exists()

HdfsTools().run()
