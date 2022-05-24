from re_common.baselibrary.baseabs import BaseAbs
from re_common.baselibrary.utils.basehdfs import BaseHDFS


class DownHdfs(object):

    def __init__(self):
        self.toml_file = "config_up.toml"
        self.dicts = {}
        self.basehdfs = None

    def read_toml(self):
        dicts = BaseAbs.get_config_factory().toml_factory().set_config_path(
            self.toml_file).read_file_remove_bom().get_dicts()
        self.dicts = dicts
        return self

    def set_basehdfs(self, i=0):
        self.basehdfs = BaseHDFS()
        self.basehdfs.localdir = self.dicts["PathPair"][i][0]
        self.basehdfs.hdfsdir = self.dicts["PathPair"][i][1]
        self.basehdfs.user_name = self.dicts["UserName"]
        self.basehdfs.namenode = self.dicts["NameNode"]
        return self

    def up_files(self):
        self.basehdfs.get_client()
        self.basehdfs.get_all_files_num()
        self.basehdfs.up_all_files()

    def use(self):
        self.read_toml()
        for i in range(len(self.dicts["PathPair"])):
            self.set_basehdfs(i)
            self.up_files()


DownHdfs().use()
