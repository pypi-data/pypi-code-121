# -*- coding:utf-8 -*-
# @Time : 2021/12/2 9:39
# @Author: suhong
# @File : TransformJournalTitleToZt.py
# @Function : 转换期刊a层到智图代码
from boto3 import Session
from re_common.facade.mysqlfacade import MysqlUtiles
from xpinyin import Pinyin
from re_common.baselibrary.utils.basetime import BaseTime


class TransformJournalTitleToZt():
    def __init__(self):
        # 初始化fields
        self.fields = [
            "lngid",
            "rawid",
            "gch",
            "title",
            "title_alternative",
            "title_series",
            "identifier_issn",
            "identifier_cnno",
            "creator",
            "creator_en",
            "creator_institution",
            "source",
            "source_en",
            "date",
            "volume",
            "issue",
            "description",
            "description_en",
            "description_fund",
            "description_core",
            "subject",
            "subject_en",
            "beginpage",
            "endpage",
            "page",
            "subject_clc",
            "date_created",
            "identifier_doi",
            "country",
            "language",
            "provider",
            "owner",
            "type",
            "medium",
            "batch",
            "provider_url",
            "provider_id",
            "if_pub1st",
            "provider_jid",
            "rawtype",
            "creator_bio",
            "cited_cnt",
            "source_id",
            "identifier_eisbn",
            "publisher",
            "jumppage",
            "identifier_pissn",
            "pagecount",
            "ref_cnt",
            "provider_subject",
            "identifier_eissn",
            "is_deprecated"
        ]
        self.BigGchMap = dict()
        self.zt_providermap = dict()
        self.param_endpoint = 'http://192.168.31.31:9000'
        self.param_access_key = 'KBWMHTMFTRF1PUT18O93'
        self.param_secret_key = 'ABSceGSwxIii2f+WQsUEl+Im4u0p+F3wpODfCJ+H'
        self.mysqlutils = MysqlUtiles(None, None, builder="MysqlBuilderForDicts", dicts={
            "host": "192.168.31.24",
            "user": "root",
            "passwd": "vipdatacenter",
            "db": "data_warehouse_sql",
            "port": "3306",
            "chartset": "utf8mb4",
        })
        self.get_gch()
        self.get_zt_provider()
        self.p = Pinyin()

    def get_zt_provider(self):
        rows = self.mysqlutils.SelectFromDB(
            "select sub_db_id,provider from a_transform_task where source_type = '3' and out_type = 'zt'")
        for row in rows[1]:
            self.zt_providermap[row[0]] = row[1]

    def get_gch(self):
        gchpath = ""
        gchmap = dict()
        sub_list = ["00002", "00393", "00004", "00006", "00169", "00451", "00452", "00288"]
        for sub_db in sub_list:
            if sub_db == "00002" or sub_db == "00393" or sub_db == "00169" or sub_db == "00451" or sub_db == "00452":
                gchpath = "suhong/gchmap/bidgch.txt"
            if sub_db == "00004" or sub_db == "00288":
                gchpath = "suhong/gchmap/qidgch.txt"
            if sub_db == "00006":
                gchpath = "suhong/gchmap/cidgch.txt"
            session = Session(aws_access_key_id=self.param_access_key,
                              aws_secret_access_key=self.param_secret_key)
            s3 = session.resource('s3', endpoint_url=self.param_endpoint)
            bucket = s3.Bucket('temp.dc.cqvip.com')
            m = bucket.Object(gchpath)
            lines = m.get()['Body'].read().decode('utf-8')
            for line in lines.split("\n"):
                if len(line) != 0:
                    gch = line.split("\t")[0].replace("\r", "").replace(" ", "")
                    r_id = line.split("\t")[1].replace("\r", "").replace(" ", "")
                    if gch == "#" or r_id == "#":
                        continue
                    gchmap[r_id] = gch
            self.BigGchMap[sub_db] = gchmap

    def format_data_create(self, publishdate, years):
        if publishdate == "" or publishdate[0:4] == "1900":
            return years + "0000"
        else:
            return publishdate

    def transform(self, titleMap):
        transMap = dict()
        journal_raw_id = titleMap.get("journal_raw_id", "")
        sub_db_id = titleMap.get("sub_db_id", "")
        transMap["lngid"] = titleMap.get("lngid", "")
        transMap["rawid"] = titleMap.get("rawid", "")
        transMap["title"] = titleMap.get("title", "")
        transMap["title_series"] = titleMap.get("column_info", "")
        transMap["title_alternative"] = titleMap.get("title_alt", "")
        if transMap["title_alternative"] == "@@":
            transMap["title_alternative"] = ""
        transMap["identifier_issn"] = titleMap.get("issn", "")
        transMap["identifier_cnno"] = titleMap.get("cnno", "")
        if sub_db_id == "00001":
            transMap["gch"] = titleMap.get("gch", "")
        else:
            try:
                transMap["gch"] = self.BigGchMap[sub_db_id].get(journal_raw_id, "")
            except:
                transMap["gch"] = ''
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_institution"] = titleMap.get("organ", "")
        transMap["source"] = titleMap.get("journal_name", "")
        transMap["source_en"] = titleMap.get("journal_name_alt", "")
        if transMap["source"] != "":
            py = self.p.get_pinyin(transMap["source"], '')
            transMap["source_fl"] = py[0]
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["volume"] = titleMap.get("vol", "")
        transMap["issue"] = titleMap.get("num", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["description_fund"] = titleMap.get("fund", "")
        transMap["description_core"] = titleMap.get("range", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["subject_clc_g1"] = titleMap.get("clc_no_1st", "")
        transMap["beginpage"] = titleMap.get("begin_page", "")
        transMap["endpage"] = titleMap.get("end_page", "")
        transMap["jumppage"] = titleMap.get("jump_page", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["date_created"] = self.format_data_create(titleMap.get("pub_date", ""), titleMap.get("pub_year", ""))
        transMap["identifier_doi"] = titleMap.get("doi", "")
        transMap["country"] = titleMap.get("country", "")
        transMap["language"] = titleMap.get("language", "")
        # transMap["provider"] = titleMap.get("zt_provider", "")
        # if transMap["provider"] == "":
        transMap["provider"] = self.zt_providermap[sub_db_id]
        transMap["type"] = titleMap.get("source_type", "")
        transMap["medium"] = "2"
        transMap["batch"] = BaseTime().get_beijin_date_strins("%Y%m%d") + "00"
        transMap["provider_url"] = transMap["provider"] + "@" + titleMap.get("provider_url")
        transMap["provider_id"] = transMap["provider"] + "@" + titleMap.get("rawid")
        transMap["if_pub1st"] = "0"
        if sub_db_id == "00393":
            transMap["if_pub1st"] = "1"
        transMap["provider_jid"] = transMap["provider"] + "@" + journal_raw_id
        transMap["rawtype"] = titleMap.get("raw_type", "")
        transMap["creator_bio"] = titleMap.get("author_intro", "")
        transMap["cited_cnt"] = titleMap.get("cited_cnt", "")
        # transMap["source_id"] = titleMap.get("journal_raw_id", "")
        transMap["identifier_eisbn"] = titleMap.get("isbn", "")
        transMap["publisher"] = titleMap.get("publisher", "")
        transMap["identifier_pissn"] = titleMap.get("issn", "")
        transMap["pagecount"] = titleMap.get("page_cnt", "")
        transMap["ref_cnt"] = titleMap.get("ref_cnt", "")
        transMap["provider_subject"] = titleMap.get("subject", "")
        transMap["identifier_eissn"] = titleMap.get("eissn", "")
        transMap["is_deprecated"] = titleMap.get("is_deprecated", "")

        for field in self.fields:
            if field not in transMap.keys():
                transMap[field] = ""
        return transMap


if __name__ == '__main__':
    t = TransformJournalTitleToZt()
