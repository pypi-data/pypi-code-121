import pypyodbc

from re_common.baselibrary.utils.baseodbc import BaseODBC
from re_common.facade.sqlite3facade import Sqlite3Utiles


class MdbDb3(object):
    """
    mdb和db3的相互转换
    """

    def __init__(self):
        self.MdbFile = ''
        self.db3file = ''
        self.baseodbc = None
        self.sqliteutils = None

    def set_mdb(self, MdbFile):
        self.MdbFile = MdbFile
        self.baseodbc = BaseODBC(self.MdbFile)
        return self

    def set_db3(self, db3_file):
        self.db3file = db3_file
        self.sqliteutils = Sqlite3Utiles().Sqlite3DBConnectFromFilePath(self.db3file)
        return self

    def get_db3_table_name(self):
        """
        获取db3的table表明
        :return:
        """
        lists_tablename = []
        for tables in self.sqliteutils.sqllite3.get_table_name():
            table = tables[0]
            lists_tablename.append(table)
        return lists_tablename

    def get_db3_fields(self, tablename):
        self.sqliteutils.sqllite3.set_result_dict()
        result = self.sqliteutils.sqllite3.get_all_field_info(tablename)
        print(result)


if __name__ == "__main__":
    md3 = MdbDb3().set_db3(r'C:\Users\xuzhu\Desktop\cnkijournallist_1628228383.4636774.db3')
    for tablename in md3.get_db3_table_name():
        md3.get_db3_fields(tablename)
