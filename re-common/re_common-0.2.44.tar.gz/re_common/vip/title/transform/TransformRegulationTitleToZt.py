# -*- coding:utf-8 -*-
# @Time : 2021/12/19 18:16
# @Author: suhong
# @File : TransformRegulationTitleToZt.py
# @Function : 法律法规a层转智图
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformRegulationTitleToZt():
    def __init__(self):
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "creator",
            "creator_en",
            "creator_release",
            "publisher",
            "date",
            "date_impl",
            "description",
            "description_en",
            "legal_status",
            "subject",
            "subject_en",
            "provider_subject",
            "identifier_standard",
            "page",
            "pagecount",
            "agency",
            "contributor",
            "description_type",
            "agents",
            "date_created",
            "rawtype",
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
            "select sub_db_id,provider from a_transform_task where source_type = '8' and out_type = 'zt'")
        for row in rows[1]:
            self.zt_providermap[row[0]] = row[1]

    def transform(self, titleMap):
        transMap = dict()
        sub_db_id = titleMap.get("sub_db_id", "")
        transMap["lngid"] = titleMap.get("lngid", "")
        transMap["rawid"] = titleMap.get("rawid", "")
        transMap["title"] = titleMap.get("title", "")
        transMap["title_alternative"] = titleMap.get("title_alt", "")
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_release"] = titleMap.get("host_organ", "")
        transMap["publisher"] = titleMap.get("final_court", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["date_impl"] = titleMap.get("impl_date", "").replace("-","")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["legal_status"] = titleMap.get("legal_status", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["provider_subject"] = titleMap.get("subject", "")
        transMap["identifier_standard"] = titleMap.get("pub_no", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["pagecount"] = titleMap.get("page_cnt", "")
        transMap["agency"] = titleMap.get("agency", "")
        transMap["contributor"] = titleMap.get("contributor", "")
        transMap["description_type"] = titleMap.get("level", "")
        transMap["agents"] = titleMap.get("agents", "")
        transMap["date_created"] = titleMap.get("pub_date", "").replace("-","")
        transMap["rawtype"] = titleMap.get("raw_type", "")
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
    t = TransformRegulationTitleToZt()

