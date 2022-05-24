from re_common.baselibrary.utils.baselist import BaseList


class JavaCodeDeal(object):

    def __init__(self):
        self.strings = """
        """
        self.lists = []
        self.baselist = BaseList()
        self.keylist = []

    def set_strings(self, strings):
        """
        设置源数据
        :param strings:
        :return:
        """
        self.strings = strings

    def strings_split(self, split="\n"):
        """
        根据条件切割为单独的数据
        :param split:
        :return:
        """
        self.lists = self.strings.split(split)

    def list_deal(self):
        """
        去除空字符串，空数据，以及字符串前后空格
        :return:
        """
        self.lists = self.baselist.remove_null(self.lists)
        self.lists = self.baselist.remove_blank_space(self.lists)
        self.lists = self.baselist.clean_space_first_end(self.lists)

    def get_key(self):
        """
        获取等号前的变量
        :return:
        """
        for item in self.lists:
            key = item.split("=")[0].replace("String", "").strip()
            self.keylist.append(key)

    def set_outmap(self):
        """
        生成outMap的put代码
        :return:
        """
        for item in self.lists:
            key = item.split("=")[0].replace("String", "").strip()
            print('outMap.put("{}", {});'.format(key, key))

    def set_sql_deal(self):
        """
        生成mysql处理代码
        :return:
        """
        for item in self.lists:
            key = item.split("=")[0].replace("String", "").strip()
            print("{} = {}.replace('\\0', ' ').replace(\"'\", \"''\").trim();".format(key, key))

    def create_sql(self):
        strinsgs = "String sql = \"INSERT INTO modify_title_info_zt("
        for key in self.keylist:
            strinsgs += "[{}],".format(key)
        strinsgs = strinsgs[:-1]
        strinsgs += ")\";"
        print(strinsgs)

    def create_s(self):
        Strings = "sql += \" VALUES ("
        for key in self.keylist:
            Strings += "'%s', "
        Strings = Strings[:-2]
        Strings += ")\";"
        print(Strings)

    def create_value(self):
        Strings = "sql = String.format(sql,"
        for key in self.keylist:
            Strings += key + ","
        Strings = Strings[:-1]
        Strings += ");"
        print(Strings)

    def create_java_sql(self):
        self.create_sql()
        self.create_s()
        self.create_value()


if __name__ == "__main__":
    strings = """
     String rawid = outMap.getOrDefault("rawid", "");
            String lngid = outMap.getOrDefault("lngid", "");
            gch = gch;
            String title = outMap.getOrDefault("rawid", "");
            String title_alternative = outMap.getOrDefault("title_alt", "");
            String identifier_issn = outMap.getOrDefault("issn", "");
            String identifier_cnno = outMap.getOrDefault("cnno", "");
            String creator = outMap.getOrDefault("author", "");
            String creator_en = outMap.getOrDefault("author_raw", "");
            String creator_institution = outMap.getOrDefault("organ", "");
            String source = outMap.getOrDefault("journal_name", "");
            String source_en = outMap.getOrDefault("journal_name_alt", "");
            String date = StringHelper.getYear(pub_year);
            String volume = outMap.getOrDefault("vol", "");
            String issue = outMap.getOrDefault("num", "");
            String description = outMap.getOrDefault("abstract", "");
            String description_en = outMap.getOrDefault("abstract_alt", "");
            String description_fund = outMap.getOrDefault("fund", "");
            String description_core = "";
            String subject = outMap.getOrDefault("keyword", "");
            String subject_en = outMap.getOrDefault("keyword_alt", "");
            String begin_page = outMap.getOrDefault("begin_page", "");
            String end_page = outMap.getOrDefault("end_page", "");
            String page = format_page(begin_page, end_page);
            String subject_clc = clc_no.replace(" ", ";").replace(",", ";");//分类号，将空格，逗号替换为分号
            String date_created = format_data_create(publishdate, pub_year);//日期，不是4位的解析出四位数字，如果是空和1900开头，改成data+0000
            String identifier_doi = outMap.getOrDefault("doi", "");
            String country = "CN";
            String language = "ZH";
            String provider = "cnkijournal";
            String owner = "cqu";
            String type = "3";
            String medium = "2";
            batch = batch;
            String provider_url = "cnkijournal@http://kns.cnki.net/KCMS/detail/detail.aspx?dbcode=CJFD&filename=" + rawid;
            String provider_id = "cnkijournal@" + rawid;
    """
    j = JavaCodeDeal()
    j.set_strings(strings)
    j.strings_split()
    j.list_deal()
    j.get_key()
    j.create_java_sql()
