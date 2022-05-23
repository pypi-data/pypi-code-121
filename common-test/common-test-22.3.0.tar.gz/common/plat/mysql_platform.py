import base64
import datetime
import json

from common.db.handle_db import MysqlDB


class MysqlPlatForm(object):

    @classmethod
    def insert_api_data(self, _url, _methond, _header, _data, _reponse_time,_reponse_code):
        _hash = hash(f'{_url}:{_methond}:{_header}:{_data}:{_reponse_time}')
        _data= str(_data).replace("'","")
        _config = {"host": "10.92.80.147", "db_name": "traffic_test", "port": 3306, "user": "mysql",
                   "password": "test1234"}
        _date=datetime.datetime.now()
        _sql=f"INSERT INTO `traffic_test`.`base_api_data`(`hash_id`, `url`,`method`, `data`, `reponse_time`,`reponse_code`, `create_time`) VALUES ('{_hash}', '{_url}', '{_methond}', '{_data}', '{_reponse_time}', '{_reponse_code}','{_date}')"
        _mysql = MysqlDB(_config)
        _mysql.execute(_sql)
        _mysql.conn.commit()
        _mysql.close()

    @classmethod
    def get_api_data(self, _url, _methond, _header, _data, _reponse_time, _reponse_code):
        _config = {"host": "10.92.80.147", "db_name": "traffic_test", "port": 3306, "user": "mysql",
                   "password": "test1234"}
        _data = str(_data).replace("'", "")
        _sql = f"select * from `traffic_test`.`base_api_data` where `url`='{_url}' and `method`='{_methond}' and `data`='{_data}' and `reponse_code`={_reponse_code} "
        _mysql = MysqlDB(_config)
        _time=''
        _info=''
        for _temp in  _mysql.execute(_sql).fetchall():
            _time=str(_temp['reponse_time'])+"S, "+_time
            _info =str(_temp['create_time']) +"执行时间:"+str(_temp['reponse_time']) + "S, " + _info
        return _time,_info


if __name__ == '__main__':

    print(MysqlPlatForm.get_api_data("http://12343.ie./iit","get","h8333","{'billCode': '12', 'billName': '行李赔偿费收据（微信版）', 'caseId': '9fc44f1cffd043aea22a58cc7c5f939b', 'data': {'accidentDetail': '测试数据pppp00000！！！   ###kkkkk看看啦啦啦', 'approver': '徐镜斯', 'baggageNo': 'abcde12345abcde12345', 'billId': None, 'billType': '12', 'caseId': '9fc44f1cffd043aea22a58cc7c5f939b', 'channelNo': '就斤斤计较哦噗噗噗0000jjj！！！', 'claimAmount': '999', 'claimReason': '测试数据从快快乐乐来了月很忙====！！！！', 'enStation': 'PVG', 'flightNoDate': 'aabbccddeeaabbccddee', 'flightRoute': 'abcdabcdabcdabcd', 'handler': 'xulong1', 'passengerName': '12345678901234567890', 'passportNo': '01234567890123456789', 'payDate': '8888kkkkiiiii坎坎坷坷', 'payer': '东航集团财务有限责任公司4444', 'planeTypeNo': None, 'psgSigner': None, 'receiveAmount': None, 'refNo': 'PVGMU11076', 'secondHandler': None, 'signDate': None, 'station': None, 'ticketNo': '12345abcde12345abcde', 'tradeNo': '88887哈哈哈哈哈kkkkk——————'}, 'saved': True}",20,200))