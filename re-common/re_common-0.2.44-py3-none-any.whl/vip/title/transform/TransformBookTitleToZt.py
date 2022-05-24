# -*- coding:utf-8 -*-
# @Time : 2021/12/19 18:16
# @Author: suhong
# @File : TransformBookTitleToZt.py
# @Function : 图书a层转智图
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformBookTitleToZt():
    def __init__(self):
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "title_sub",
            "title_edition",
            "title_series",
            "identifier_eisbn",
            "identifier_pisbn",
            "identifier_doi",
            "creator",
            "creator_en",
            "creator_bio",
            "creator_institution",
            "publisher",
            "date",
            "description",
            "description_en",
            "description_unit",
            "subject",
            "subject_en",
            "subject_clc",
            "subject_esc",
            "page",
            "beginpage",
            "endpage",
            "pagecount",
            "date_created",
            "rawtype",
            "folio_size",
            "price",
            "pub_place",
            "language",
            "country",
            "type",
            "provider",
            "provider_url",
            "provider_id",
            "medium",
            "batch",
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
            "select sub_db_id,provider from a_transform_task where source_type = '1' and out_type = 'zt'")
        for row in rows[1]:
            self.zt_providermap[row[0]] = row[1]

    def transform(self, titleMap):
        transMap = dict()
        sub_db_id = titleMap.get("sub_db_id", "")
        transMap["lngid"] = titleMap.get("lngid", "")
        transMap["rawid"] = titleMap.get("rawid", "")
        transMap["title"] = titleMap.get("title", "")
        transMap["title_alternative"] = titleMap.get("title_alt", "")
        transMap["title_series"] = titleMap.get("title_series", "")
        transMap["title_edition"] = titleMap.get("revision", "")
        transMap["identifier_eisbn"] = titleMap.get("eisbn", "")
        transMap["identifier_pisbn"] = titleMap.get("isbn", "")
        transMap["identifier_doi"] = titleMap.get("doi", "")
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_institution"] = titleMap.get("organ", "")
        transMap["creator_bio"] = titleMap.get("author_intro", "")
        transMap["publisher"] = titleMap.get("publisher", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["description_unit"] = titleMap.get("catalog", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["subject_esc"] = titleMap.get("subject_edu", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["beginpage"] = titleMap.get("begin_page", "")
        transMap["endpage"] = titleMap.get("end_page", "")
        transMap["pagecount"] = titleMap.get("page_cnt", "")
        transMap["date_created"] = titleMap.get("pub_date", "")
        transMap["rawtype"] = titleMap.get("raw_type", "")
        transMap["folio_size"] = titleMap.get("book_size", "")
        transMap["price"] = titleMap.get("price", "")
        transMap["pub_place"] = titleMap.get("pub_place", "")
        # transMap["provider"] = titleMap.get("zt_provider", "")
        # if transMap["provider"] == "":
        transMap["provider"] = self.zt_providermap[sub_db_id]
        transMap["provider_url"] = transMap["provider"] + "@" + titleMap.get("provider_url")
        transMap["provider_id"] = transMap["provider"] + "@" + titleMap.get("rawid")
        transMap["batch"] = BaseTime().get_beijin_date_strins("%Y%m%d") + "00"
        transMap["type"] = titleMap.get("source_type", "")
        transMap["medium"] = "2"
        transMap["country"] = titleMap.get("country", "")
        transMap["language"] = titleMap.get("language", "")
        transMap["is_deprecated"] = titleMap.get("is_deprecated", "")

        for field in self.fields:
            if field not in transMap.keys():
                transMap[field] = ""
        return transMap

if __name__ == '__main__':
    t = TransformBookTitleToZt()
