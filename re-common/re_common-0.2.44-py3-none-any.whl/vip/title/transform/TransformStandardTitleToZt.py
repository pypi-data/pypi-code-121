# -*- coding:utf-8 -*-
# @Time : 2021/12/21 13:47
# @Author: suhong
# @File : TransformStandardTitleToZt.py
# @Function : 标准a层转智图
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformStandardTitleToZt():
    def __init__(self):
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "identifier_standard",
            "identifier_doi",
            "creator",
            "creator_en",
            "creator_institution",
            "creator_release",
            "date",
            "date_impl",
            "date_created",
            "description",
            "description_en",
            "description_type",
            "subject",
            "subject_en",
            "page",
            "subject_clc",
            "subject_esc",
            "subject_csc",
            "subject_isc",
            "legal_status",
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
            "select sub_db_id,provider from a_transform_task where source_type = '5' and out_type = 'zt'")
        for row in rows[1]:
            self.zt_providermap[row[0]] = row[1]

    def transform(self, titleMap):
        transMap = dict()
        sub_db_id = titleMap.get("sub_db_id", "")
        transMap["lngid"] = titleMap.get("lngid", "")
        transMap["rawid"] = titleMap.get("rawid", "")
        transMap["title"] = titleMap.get("title", "")
        transMap["title_alternative"] = titleMap.get("title_alt", "")
        transMap["identifier_standard"] = titleMap.get("std_no", "")
        transMap["identifier_doi"] = titleMap.get("doi", "")
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_institution"] = titleMap.get("organ", "")
        transMap["creator_release"] = titleMap.get("publisher", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["date_impl"] = titleMap.get("impl_date", "")
        transMap["date_created"] = titleMap.get("pub_date", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["description_type"] = titleMap.get("raw_type", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["page"] = titleMap.get("page_info", "")
        transMap["pagecount"] = titleMap.get("page_cnt", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["subject_esc"] = titleMap.get("subject_edu", "")
        transMap["subject_csc"] = titleMap.get("ccs_no", "")
        transMap["subject_isc"] = titleMap.get("ics_no", "")
        transMap["legal_status"] = titleMap.get("legal_status", "")
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
    t = TransformStandardTitleToZt()
    filePath = r"D:\Tencent\WorkWeChat\WXWork\1688853051796109\Cache\File\2022-01\a_bz_20210104.txt"
    insert_list = list()
    insert_db3_path = "./zt_wanfangstandard_00030_update_20220104.db3"
    import json,sqlite3
    import pandas as pd
    with open(filePath, "r", encoding="utf-8") as file_to_read:
        while True:
            fLine = file_to_read.readline()
            xx = fLine.strip()
            try:
                data = json.loads(xx)
                new_data = t.transform(data)
                insert_list.append(new_data)
                if len(insert_list) >= 1000:
                    insert_conn = sqlite3.connect(insert_db3_path, check_same_thread=False)
                    pd.DataFrame(insert_list).to_sql("modify_title_info_zt", insert_conn, if_exists='append',
                                                     index=False)
                    insert_list.clear()
            except:
                print(xx)

            if not fLine:
                break


