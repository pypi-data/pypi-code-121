"""
不想写循环代码  生成循环代码
"""
from re_common.baselibrary.utils.basedir import BaseDir
from re_common.baselibrary.utils.basefile import BaseFile


class CreateCode():

    def __init__(self):
        self.inputobj1 = set()

    def read_file(self, filepath):
        for file in BaseDir.get_dir_all_files(filepath):
            for line in BaseFile.read_file_r_mode_yield(file):
                if line.find("String") > -1:
                    var = line.split("=")[0].replace("String", "").strip()
                    self.inputobj1.add(var)
            yield file

    def create_code(self, file):
        with open(file, mode="w", encoding="utf-8") as f:
            for var in self.inputobj1:
                f.write("if (updateItem.getKey().equals(\"%s\")) {\n" % var)
                f.write("    {} = updateItem.getValue().trim();\n".format(var))
                f.write("}\n")

    def create_put(self, file):
        with open(file, mode="w", encoding="utf-8") as f:
            for var in self.inputobj1:
                f.write("xObj_a_table.data.put(\"%s\", %s);\n" % (var,var))

    def create_replace(self, file):
        with open(file, mode="w", encoding="utf-8") as f:
            for var in self.inputobj1:
                f.write("%s = %s.replace('\\0', ' ').replace(\"'\", \"''\").trim();\n" % (var, var))

    def set_to_list(self):
        self.inputs1 = list(self.inputobj1)

    def create_sql(self,file):
        with open(file, mode="w", encoding="utf-8") as f:
            strinsgs = "String sql = \"INSERT INTO modify_title_info_zt("
            for key in self.inputs1:
                strinsgs += "[{}],".format(key)
            strinsgs = strinsgs[:-1]
            strinsgs += ")\";"
            f.write(strinsgs)

    def create_s(self):
        Strings = "sql += \" VALUES ("
        for key in self.inputs1:
            Strings += "'%s', "
        Strings = Strings[:-2]
        Strings += ")\";"
        print(Strings)

    def create_value(self):
        Strings = "sql = String.format(sql,"
        for key in self.inputs1:
            Strings += key+","
        Strings = Strings[:-1]
        Strings += ");"
        print(Strings)


if __name__ == "__main__":
    createcode = CreateCode()
    for file in createcode.read_file(r"./inputs"):
        createcode.set_to_list()
        # createcode.create_replace(file.replace("input", "output"))
        # createcode.create_code(file.replace("input", "output"))
        createcode.create_put(file.replace("input", "output"))
        # createcode.set_to_list()
        # createcode.create_sql(file.replace("input", "output"))
        # createcode.create_s()
        # createcode.create_value()


