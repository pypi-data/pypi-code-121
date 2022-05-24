# -*- coding:utf-8 -*-
# @Time : 2021/12/15 14:09
# @Author: suhong
# @File : TransformConferenceTitleToZt.py
# @Function :转换会议a层到智图代码
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformConferenceTitleToZt():
    def __init__(self):
        # 初始化fields
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "title_series",
            "title_edition",
            "applicant",
            "identifier_doi",
            "creator",
            "creator_en",
            "creator_institution",
            "creator_bio",
            "creator_drafting",
            "creator_release",
            "source",
            "source_en",
            "source_institution",
            "publisher",
            "date",
            "description",
            "description_en",
            "description_fund",
            "subject",
            "subject_en",
            "page",
            "beginpage",
            "endpage",
            "jumppage",
            "pagecount",
            "subject_clc",
            "subject_esc",
            "date_created",
            "pub_place",
            "language",
            "country",
            "type",
            "provider",
            "provider_url",
            "provider_id",
            "medium",
            "batch",
            "is_deprecated",
            "if_pdf_fulltext",
            "if_html_fulltext"
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
            "select sub_db_id,provider from a_transform_task where source_type = '6' and out_type = 'zt'")
        for row in rows[1]:
            self.zt_providermap[row[0]] = row[1]

    def transform(self, titleMap):
        transMap = dict()
        sub_db_id = titleMap.get("sub_db_id", "")
        transMap["lngid"] = titleMap.get("lngid", "")
        transMap["rawid"] = titleMap.get("rawid", "")
        transMap["title"] = titleMap.get("title", "")
        transMap["title_alternative"] = titleMap.get("title_alt", "")
        transMap["title_series"] = titleMap.get("meeting_record_name", "")
        transMap["title_edition"] = titleMap.get("revision", "")
        transMap["applicant"] = titleMap.get("applicant", "")
        transMap["identifier_doi"] = titleMap.get("doi", "")
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_institution"] = titleMap.get("organ", "")
        transMap["creator_bio"] = titleMap.get("author_intro", "")
        transMap["creator_drafting"] = titleMap.get("society", "")
        transMap["creator_release"] = titleMap.get("host_organ", "")
        transMap["source"] = titleMap.get("meeting_name", "")
        transMap["source_en"] = titleMap.get("meeting_name_alt", "")
        transMap["source_institution"] = titleMap.get("meeting_place", "")
        transMap["publisher"] = titleMap.get("publisher", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["description_fund"] = titleMap.get("fund", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["beginpage"] = titleMap.get("begin_page", "")
        transMap["endpage"] = titleMap.get("end_page", "")
        transMap["jumppage"] = titleMap.get("jump_page", "")
        transMap["pagecount"] = titleMap.get("page_cnt", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["subject_esc"] = titleMap.get("subject_edu", "")
        transMap["date_created"] = titleMap.get("pub_date", "")
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
        fulltext_type = titleMap.get("fulltext_type", "")
        transMap["if_pdf_fulltext"] = "0"
        transMap["if_html_fulltext"] = "0"
        if "pdf" in fulltext_type:
            transMap["if_pdf_fulltext"] = "1"
        if "html" in fulltext_type:
            transMap["if_html_fulltext"] = "1"
        transMap["is_deprecated"] = titleMap.get("is_deprecated", "")

        for field in self.fields:
            if field not in transMap.keys():
                transMap[field] = ""
        return transMap


if __name__ == '__main__':
    t = TransformConferenceTitleToZt()
