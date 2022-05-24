# -*- coding:utf-8 -*-
# @Time : 2021/12/15 14:09
# @Author: suhong
# @File : TransformThesisTitleToZt.py
# @Function :转换博硕a层到智图代码
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformThesisTitleToZt():
    def __init__(self):
        # 初始化fields
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "title_sub",
            "identifier_doi",
            "creator",
            "creator_en",
            "creator_bio",
            "creator_degree",
            "creator_discipline",
            "creator_institution",
            "contributor",
            "description",
            "description_en"
            "subject",
            "subject_en",
            "subject_clc",
            "subject_esc",
            "subject_dsa",
            "date",
            "date_created",
            "provider",
            "provider_url",
            "provider_id",
            "description_fund",
            "page",
            "beginpage",
            "endpage",
            "jumppage",
            "pagecount",
            "batch",
            "type",
            "rawtype",
            "medium",
            "language",
            "country",
            "provider_subject",
            "identifier_pisbn",
            "identifier_eisbn",
            "price",
            "pub_place",
            "is_deprecated"
        ]
        self.zt_providermap = dict()
        self.mysqlutils = MysqlUtiles(None, None, builder="MysqlBuilderForDicts", dicts={
            "host": "192.168.31.24",
            "user": "root",
            "passwd": "vipdatacenter",
            "db": "data_warehouse_sql",
            "port": "3306",
            "chartset": "utf8mb4",
        })
        self.get_zt_provider()

    def get_zt_provider(self):
        rows = self.mysqlutils.SelectFromDB(
            "select sub_db_id,provider from a_transform_task where source_type = '4' and out_type = 'zt'")
        for row in rows[1]:
            self.zt_providermap[row[0]] = row[1]

    def transform(self, titleMap):
        transMap = dict()
        sub_db_id = titleMap.get("sub_db_id", "")
        transMap["lngid"] = titleMap.get("lngid", "")
        transMap["rawid"] = titleMap.get("rawid", "")
        transMap["title"] = titleMap.get("title", "")
        transMap["title_alternative"] = titleMap.get("title_alt", "")
        transMap["title_sub"] = titleMap.get("title_sub", "")
        transMap["identifier_doi"] = titleMap.get("doi", "")
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_bio"] = titleMap.get("author_intro", "")
        transMap["creator_degree"] = titleMap.get("degree", "")
        transMap["creator_discipline"] = titleMap.get("subject_major", "")
        if transMap["creator_discipline"] == "":
            transMap["creator_discipline"] = titleMap.get("subject_dsa", "")
        transMap["creator_institution"] = titleMap.get("organ", "")
        transMap["contributor"] = titleMap.get("contributor", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["subject_esc"] = titleMap.get("subject_edu", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["date_created"] = titleMap.get("pub_date", "")
        # transMap["provider"] = titleMap.get("zt_provider", "")
        # if transMap["provider"] == "":
        transMap["provider"] = self.zt_providermap[sub_db_id]
        transMap["provider_url"] = transMap["provider"] + "@" + titleMap.get("provider_url")
        transMap["provider_id"] = transMap["provider"] + "@" + titleMap.get("rawid")
        transMap["description_fund"] = titleMap.get("fund", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["beginpage"] = titleMap.get("begin_page", "")
        transMap["endpage"] = titleMap.get("end_page", "")
        transMap["jumppage"] = titleMap.get("jump_page", "")
        transMap["pagecount"] = titleMap.get("page_cnt", "")
        transMap["batch"] = BaseTime().get_beijin_date_strins("%Y%m%d") + "00"
        transMap["type"] = titleMap.get("source_type", "")
        transMap["rawtype"] = titleMap.get("raw_type", "")
        transMap["medium"] = "2"
        transMap["country"] = titleMap.get("country", "")
        transMap["language"] = titleMap.get("language", "")
        transMap["provider_subject"] = titleMap.get("sub_db_class_name", "")
        transMap["identifier_pisbn"] = titleMap.get("isbn", "")
        transMap["identifier_eisbn"] = titleMap.get("eisbn", "")
        transMap["price"] = titleMap.get("price", "")
        transMap["pub_place"] = titleMap.get("pub_place", "")
        transMap["is_deprecated"] = titleMap.get("is_deprecated", "")

        for field in self.fields:
            if field not in transMap.keys():
                transMap[field] = ""
        return transMap

if __name__ == '__main__':
    t = TransformThesisTitleToZt()



