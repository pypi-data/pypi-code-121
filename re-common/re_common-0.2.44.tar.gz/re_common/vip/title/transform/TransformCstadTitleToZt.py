# -*- coding:utf-8 -*-
# @Time : 2021/12/19 18:17
# @Author: suhong
# @File : TransformCstadTitleToZt.py
# @Function : 成果a层转智图
from re_common.baselibrary.utils.basetime import BaseTime

from re_common.facade.mysqlfacade import MysqlUtiles


class TransformCstadTitleToZt():
    def __init__(self):
        # 初始化fields
        self.fields = [
            "lngid",
            "rawid",
            "title",
            "title_alternative",
            "title_series",
            "title_edition",
            "identifier_doi",
            "creator",
            "creator_en",
            "creator_institution",
            "creator_bio",
            "description",
            "description_en",
            "subject",
            "subject_en",
            "date",
            "date_created",
            "subject_clc",
            "subject_esc",
            "description_type",
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
            "select sub_db_id,provider from a_transform_task where source_type = '9' and out_type = 'zt'")
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
        transMap["identifier_doi"] = titleMap.get("doi", "")
        transMap["creator"] = titleMap.get("author", "")
        transMap["creator_en"] = titleMap.get("author_alt", "")
        transMap["creator_institution"] = titleMap.get("organ", "")
        transMap["creator_bio"] = titleMap.get("author_intro", "")
        transMap["description"] = titleMap.get("abstract", "")
        transMap["description_en"] = titleMap.get("abstract_alt", "")
        transMap["subject"] = titleMap.get("keyword", "")
        transMap["subject_en"] = titleMap.get("keyword_alt", "")
        transMap["date"] = titleMap.get("pub_year", "")
        transMap["date_created"] = titleMap.get("pub_date", "")
        transMap["subject_clc"] = titleMap.get("clc_no", "")
        transMap["subject_esc"] = titleMap.get("subject_edu", "")
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
    t = TransformCstadTitleToZt()
    data = {
      "_id": "00275FCILN8O9JP1MPDO8IP067BG0ILZ",
      "applicant_organ": "",
      "sub_db": "SNAD",
      "country": "CN",
      "register_no": "",
      "clc_machine": "",
      "subject": "",
      "rawid_alt": "",
      "recommend_organ_code": "",
      "transfer_terms": "",
      "language": "ZH",
      "from_to_date": "2016-10～2018-09",
      "investment_amount": "",
      "std_no": "",
      "latest_date": "20210120",
      "clc_no": "R472.2",
      "app_date": "",
      "keyword": "ICU;获得性;干预策略;集束化",
      "investment_explain": "",
      "transfer_annotation": "",
      "fax": "",
      "save_money": "",
      "patent_cnt": "",
      "lngid": "00275FCILN8O9JP1MPDO8IP067BG0ILZ",
      "level": "",
      "author": "徐玲芬;谢波;周庆;姬晓伟;李敏;钟玉英;钟瑞英;姜勤;刘晓博",
      "sub_db_id": "00275",
      "postcode": "",
      "batch": "20201010_103123;20210607_085602",
      "keyid": "00275FCILN8O9JP1MPDO8IP067BG0ILZ",
      "down_date": "20201010;20201010",
      "source_type": "9",
      "tax": "",
      "provider_url": "https://kns.cnki.net/kcms/detail/detail.aspx?dbname=SNAD&filename=SNAD000001839999",
      "transfer_scope": "",
      "plan_name": "",
      "organ_alt": "",
      "vision": "1",
      "subject_edu": "320.71",
      "rawid": "SNAD000001839999",
      "subject_word": "",
      "investment_annotation": "",
      "trade_no": "",
      "author_id": "",
      "build_duration": "",
      "organ_area": "",
      "organ": "湖州市中心医院",
      "recommend_no": "",
      "authorization_no": "",
      "corr_organ_addr": "",
      "spread_explain": "",
      "title": "基于循证构建ICU获得性衰弱集束化干预策略及其应用研究",
      "keyword_alt": "",
      "trade_name": "",
      "identify_organ": "",
      "abstract_alt": "",
      "pub_date": "20200000",
      "provider": "CNKI",
      "pub_year": "2020",
      "fulltext_type": "",
      "corr_author": "",
      "recommend_date": "",
      "clc_no_1st": "R472.2",
      "email": "",
      "product": "CNKI",
      "keyword_machine": "",
      "recommend_organ": "",
      "earn_foreign": "",
      "identify_date": "",
      "spread_form": "",
      "register_date": "",
      "evaluation_form": "验收",
      "abstract": "一、主要研究内容  1.基于循证理论,探索目前适合我国对ICU获得性衰弱患者有效的集束化干预策略。 2.研究本策略对提高ICU获得性衰弱患者肌力、改善生活自理能力、缩短ICU入住时间、住院时间及机械通气时间等的影响。 3.建立多学科医护团队,培养一支能够改善ICU获得性衰弱患者预后的优良医护队伍。   二、主要创新点  1.该策略的制定是在循证的基础上,经过相关领域知名专家的二轮的论证而确立,具有较强的科学性和实用性。将该干预策略应用于临床实践,真正解决临床实际问题。 2.集束化干预策略的应用,优化了传统单一护理措施的模式,将循证所得的综合措施应用于临床护理实践,为患者提供优质的护理服务,也为从事ICU临床护理工作的同行提供了可借鉴的经验。 3.本研究涉及多学科医护专业人员,通过彼此的合作,旨在培养一支具有良好业务素质、能够有效改善ICUAW患者预后的优良的医护团队。   三、主要技术、经济指标(执行期内和产业化阶段的要分开)  1.拟达到的主要技术指标:①提高ICU获得性衰弱患者肌力、生活自理能力、缩短ICU获得性衰弱患者住院时间,缩短患者机械通气天数。②促进患者疾病康复,为临床培养一支能够改善ICU获得性衰弱患者疾病预后的优良医护团队。③在核心期刊发表高质量研究论文2篇。 2.主要经济指标：ICU获得性衰弱集束化干预策略的实施,可缩短ICU获得性衰弱患者入住ICU时间及住院时间、有效降低患者医疗费用、节约医疗资源,具有显著的经济效益。",
      "fulltext_addr": "",
      "transfer_content": "",
      "register_organ": "",
      "transfer_fee": "",
      "corr_organ": "",
      "accept_date": "20200000",
      "is_deprecated": "0",
      "title_alt": "",
      "raw_type": "应用技术",
      "restricted": "",
      "transfer_form": "",
      "spread_scope": "",
      "spread_track": "",
      "output_value": "",
      "app_no": "",
      "author_alt": "",
      "organ_id": ""
    }
    print(t.transform(data))