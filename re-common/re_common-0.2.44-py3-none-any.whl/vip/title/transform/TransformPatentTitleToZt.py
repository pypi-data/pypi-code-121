# -*- coding:utf-8 -*-
# @Time : 2021/12/15 14:09
# @Author: suhong
# @File : TransformPantentTitleToZt.py
# @Function :转换专利层到智图代码
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformPantentTitleToZt():
    def __init__(self):
        # 初始化fields
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "creator",
            "creator_en",
            "creator_bio",
            "creator_institution",
            "applicant",
            "date",
            "description",
            "description_en",
            "subject",
            "subject_en",
            "subject_clc",
            "subject_esc",
            "subject_isc",
            "subject_csc",
            "date_created",
            "agency",
            "agents",
            "description_core",
            "legal_status",
            "pct_app_data",
            "pct_enter_nation_date",
            "pct_pub_data",
            "priority_number",
            "identifier_pissn",
            "date_impl",
            "identifier_standard",
            "province_code",
            "page",
            "description_type",
            "cited_cnt",
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
            "select sub_db_id,provider from a_transform_task where source_type = '7' and out_type = 'zt'")
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
        transMap["creator_bio"] = titleMap.get("author_intro", "")
        transMap["creator_institution"] = titleMap.get("applicant_addr", "")
        transMap["applicant"] = titleMap.get("applicant", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["subject_esc"] = titleMap.get("subject_edu", "")
        transMap["subject_isc"] = titleMap.get("ipc_no", "")
        transMap["subject_csc"] = titleMap.get("ipc_no_1st", "")
        transMap["date_created"] = titleMap.get("pub_date", "")
        transMap["agency"] = titleMap.get("agency", "")
        transMap["agent"] = titleMap.get("agent", "")
        transMap["description_core"] = titleMap.get("claim", "")
        transMap["legal_status"] = titleMap.get("legal_status", "")
        transMap["pct_app_data"] = titleMap.get("pct_app_data", "")
        transMap["pct_enter_nation_date"] = titleMap.get("pct_enter_nation_date", "")
        transMap["pct_pub_data"] = titleMap.get("pct_pub_data", "")
        transMap["priority_number"] = titleMap.get("priority_no", "")
        transMap["identifier_pissn"] = titleMap.get("app_no", "")
        transMap["date_impl"] = titleMap.get("app_date", "")
        transMap["identifier_standard"] = titleMap.get("pub_no", "")
        transMap["province_code"] = titleMap.get("organ_area", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["description_type"] = titleMap.get("raw_type", "")
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
    t = TransformPantentTitleToZt()
