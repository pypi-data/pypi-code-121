#!/usr/bin/env python
# -*- coding: utf-8 -*-

import logging
import os
import sys
import time
import tornado.gen
from tornado.ioloop import IOLoop
from lycium.asynchttphandler import async_route, args_as_dict, request_body_as_json
from lycium.dbproxy import DbProxy
from lycium.webapplication import WebApplication

logging.basicConfig(stream=sys.stdout, level=logging.DEBUG)

rdbms = {}
mongodbs = {}

from .builtin_dbconfig import *
try:
    from .local_dbconfig import *
except:
    pass

from mongoengine import (BooleanField, DateTimeField, Document, FloatField,
                         IntField, ReferenceField, StringField, ObjectIdField)
import datetime
from lycium.modelutils import MongoBase

class XHHK_Application(MongoBase):
    type = StringField()  # 1-区域审方中心 11-公立医院 12-私立医 13-互联网医院 21-药房
    name = StringField()
    code = StringField()
    level = StringField()  # 级别
    cooperation_mode = IntField(default=1)  # 合作方式
    expire_time = DateTimeField(default=0)
    sign = StringField()  # 签名
    lng = StringField()  # 经度
    lat = StringField()  # 纬度
    appKey = StringField()  # 鉴权key
    telphone = StringField()
    address = StringField()
    distribution = IntField(default=0)  # 是否支持配送，0-不配送，1-院内配送，2-院外配送
    admin_user_id = ObjectIdField()
    business_license = StringField()
    contacts = StringField()

    obsoleted = BooleanField(default=False)
    created_at = FloatField(default=time.time() * 1000)
    updated_at = FloatField(default=time.time() * 1000)
    created_by = StringField()
    updated_by = StringField()
    sort_value = IntField(default=1)

    meta = {
        'collection': 'XHHK_Application',  # 指定collection的名字
        'indexes': [
            ('code'),
        ]
    }

    def all_fields(self):
        data = {}
        data['id'] = str(self.id)
        data['type'] = self.type
        data['name'] = self.name
        data['code'] = self.code
        data['level'] = self.level
        data['cooperation_mode'] = self.cooperation_mode
        expire_time = ''
        if self.expire_time != 0:
            expire_time = self.expire_time.strftime('%Y-%m-%d %H:%M:%S')
        data['expire_time'] = expire_time
        sign = ''
        if self.sign:
            sign = self.sign
        data['sign'] = sign
        data['lng'] = self.lng
        data['lat'] = self.lat
        data['appKey'] = self.appKey
        data['obsoleted'] = self.obsoleted
        data['created_at'] = self.created_at
        data['updated_at'] = self.updated_at
        created_by = ''
        if self.created_by:
            created_by = self.created_by
        data['created_by'] = created_by
        updated_by = ''
        if self.updated_by:
            updated_by = self.updated_by
        data['updated_by'] = updated_by
        data['sort_value'] = self.sort_value

        return data

class XHHK_Person(MongoBase):
    app_id = ReferenceField(XHHK_Application)
    type = IntField()                   # 0其他，1药师，2医生，3护士
    name = StringField()
    employee_number = StringField()
    his_code = StringField()
    id_number = StringField()         # 身份证
    occupation_no = StringField()   # 资格证号
    title = StringField()
    sign = StringField()             # 签名
    dept_code = StringField()        # 科室
    gender = StringField()           # 性别，1男2女
    telephone = StringField()        # 手机
    birthdate = IntField()            # 生日
    country = IntField()            # 国家
    post = StringField()            # 职务
    pydm = StringField()             # 拼音代码
    routing_key = StringField()      #
    wx_open_id = StringField()       # 微信openid
    antibac_level = IntField()       # 抗菌药物权限
    pres_right = IntField()          # 开方权限
    psych_level = IntField()         # 麻醉药权限
    narcotic_level = IntField()      # 精神药权限
    image = StringField()

    obsoleted = BooleanField(default=False)
    created_at = FloatField(default=time.time()*1000)
    updated_at = FloatField(default=time.time()*1000)
    created_by = StringField()
    updated_by = StringField()
    sort_value = IntField(default=1)

    meta = {
        'collection': 'XHHK_Person',    #指定collection的名字
        'ordering': ['-updated_at'],
        'indexes': [
            ('employee_number'),
            ('id_number'),
            ('telephone'),
            ('pydm'),
            ('his_code'),
        ]
    }

class SFLZ_Prescription(MongoBase):
    patient_id = ObjectIdField()
    app_id = ReferenceField(XHHK_Application)
    merchant_id = ObjectIdField()
    visit_id = ObjectIdField()
    prescription_code = StringField()   # 处方号
    prescription_time = DateTimeField() # 处方时间
    prescription_type = IntField()   # 处方类型
    doct_id = ReferenceField(XHHK_Person)    # 医生
    phar_id = ReferenceField(XHHK_Person)    # 审核药师
    team_id = ObjectIdField()
    dept_code = StringField()               # 科室
    mix_phar = StringField()            # 调配药师
    dispensing_phar = StringField()    # 发药药师

    audits_id = ReferenceField(XHHK_Application)    # 审核机构ID
    audit_status = IntField(default=0)      # 审核状态
    audit_starttime = DateTimeField()       # 审方开始
    audit_endtime = DateTimeField()         # 审方结束
    status = StringField(default='1')       # 处方状态：'-1'已作废（同obsoleted），'1'新开，'2'已审核，'3'已打印，'4'已缴费，'5'已取药，'6'已退费，'8'未知，'9'已删除
    reason = StringField()
    total_price = FloatField(default=-1)
    transferable = IntField(default=-1)
    qrcode = StringField(default='')              # 处方二维码
    pay_type = StringField(default='')               # 医保类别
    fee_type = StringField()                    # 费别 
    cn_west_flag = StringField(default='1')     # 1西药处方 2中成药处方 3中草药处方
    package_number = IntField(default=1)        # 剂数
    remark = StringField(default='')            # 处方备注
    agent_name = StringField()                  # 代办人
    agent_idnumber = StringField()              # 代办人身份证号
    invoice_code = StringField()                # 发票号码
    dispensing_window = StringField()           # 取药窗口
    user_del = BooleanField()
    medicine_type_count = IntField()            # 药品种数
    order_id = ObjectIdField()                  # 订单id
    access_time = IntField()                    # 取药时间，ms时间戳

    antibacterial = IntField(default=0) # 抗菌
    antitumor = IntField(default=0)     # 抗癌
    psychotropic = IntField(default=0)  # 精神
    narcotic = IntField(default=0)      # 麻醉
    toxic = IntField(default=0)         # 毒性
    basic = IntField(default=0)         # 基药
    injection = IntField(default=0)     # 注射液
    expensive = IntField(default=0)     # 高价

    obsoleted = BooleanField(default=False)
    created_at = FloatField(default=time.time() * 1000)
    updated_at = FloatField(default=time.time() * 1000)
    updated_by = StringField()
    sort_value = IntField(default=1)

    meta = {
        'collection': 'SFLZ_Prescription',  # 指定collection的名字
        'ordering': ['-updated_at'],
        'indexes': [
            ('patient_id'),
            ('app_id'),
            ('merchant_id'),
            ('visit_id'),
            ('prescription_code'),
            ('prescription_time'),
            ('prescription_type'),
            ('doct_id'),
            ('phar_id'),
            ('audits_id'),
            ('audit_status'),
            ('transferable'),

            ('antibacterial'),
            ('antitumor'),
            ('psychotropic'),
            ('narcotic'),
            ('toxic'),
            ('basic'),
            ('injection'),
            ('expensive'),
        ]
    }

@async_route('/healthz', methods=['GET'])
@tornado.gen.coroutine
def test_healthz(handler, request):
    return 'hello'

@async_route('/debug', methods=['GET'])
@tornado.gen.coroutine
def test_query_mongo(handler, request):
    t1 = time.time()
    print(' << access on %s' % (time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(t1))))
    date_str = datetime.datetime.strptime((datetime.datetime.now() - datetime.timedelta(days=41)).strftime("%Y-%m-%d"), "%Y-%m-%d")
    result = yield DbProxy().query_all_mongo(SFLZ_Prescription,
                                       filters={"prescription_time__gte": date_str, "obsoleted": False},
                                       limit=None
                                      )
    t2 = time.time()
    print(" -- records:%d dt %.2f" % (len(result), t2 - t1))
    return 'done'

def test_mongodb_api():
    DbProxy().setup_rdbms(rdbms)
    DbProxy().setup_mongodbs(mongodbs)

    web_app = WebApplication()
    web_app.listen(port=8081, address='0.0.0.0')
    print('starting...')
    IOLoop.instance().start()

if __name__ == "__main__":
    test_mongodb_api()
