import time
import requests
import json,os


class WeChat_SMS:
    def __init__(self,corpsecret = '_4vuUmRxg9V5bnb1dZ2QlhHIBiwIL5O7SMvowRX7_WA',agentid = '1000002',partid='0'):
        self._corpid = 'ww97a5a59259fbb43d'#企业ID， 登陆企业微信，在我的企业-->企业信息里查看
        self._corpsecret = corpsecret#自建应用，每个自建应用里都有单独的secret
        self._agentid = agentid #应用代码
        self._partid = partid


    @property
    def CorpId(self):
        return self._corpid
        
    @CorpId.setter
    def CorpId(self,value):
        self._corpid = value
        
    @property
    def CorpSecret(self):
        return _corpsecret
        
    @CorpSecret.setter
    def CorpSecret(self,value):
        self._corpsecret = value
        
    @property
    def AgentId(self):
        return _agentid
        
    @AgentId.setter
    def AgentId(self,value):
        self._agentid = value
        

    def _get_access_token(self):
        url = 'https://qyapi.weixin.qq.com/cgi-bin/gettoken'
        values = {'corpid': self._corpid,'corpsecret': self._corpsecret,}
        req = requests.post(url, params=values)
        data = json.loads(req.text)
        return data["access_token"]

    def get_access_token(self):
        try:
            with open('access_token_{0}.conf'.format(self._agentid), 'r') as f:
                t, access_token = f.read().split()
        except:
            with open('access_token_{0}.conf'.format(self._agentid), 'w') as f:
                access_token = self._get_access_token()
                cur_time = time.time()
                f.write('\t'.join([str(cur_time), access_token]))
                return access_token
        else:
            cur_time = time.time()
            if 0 < cur_time - float(t) < 7200:#token的有效时间7200s
                return access_token
            else:
                with open('access_token_{0}.conf'.format(self._agentid), 'w') as f:
                    access_token = self._get_access_token()
                    f.write('\t'.join([str(cur_time), access_token]))
                    return access_token

    def send_data(self, msg,user='@all'):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser": user,
            "toparty": self._partid,     #设置给部门发送
            "msgtype": "text",
            "agentid": self._agentid,
            "text": {
            "content": msg
            },
            "safe": "0"
        }
        send_msges=(bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()#当返回的数据是json串的时候直接用.json即可将respone转换成字典
        #print (respone["errmsg"])
        return respone["errmsg"]
        
    def send_taskcard(self,msg,user='@all'):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser" : user,
            "toparty" : self._partid,
            #"totag" : "TagID1 | TagID2",
            "msgtype" : "taskcard",
            "agentid" : self._agentid,
            "taskcard" : {
                "title" : "赵明登的礼物申请",
                "description" : "礼品：A31茶具套装<br>用途：赠与小黑科技张总经理",
                "url" : "http://119.3.254.8/todo",
                "task_id" : "task1234",
                "btn":[
                    {
                        "key": "key111",
                        "name": "批准",
                        "replace_name": "已批准",
                        "color":"red",
                        "is_bold": True
                    },
                    {
                        "key": "key222",
                        "name": "驳回",
                        "replace_name": "已驳回"
                    }
                ]
            },
        #"enable_id_trans": 0,
        #"enable_duplicate_check": 0,
        #"duplicate_check_interval": 1800
        "safe":"0"
        }
        send_msges=(bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()#当返回的数据是json串的时候直接用.json即可将respone转换成字典
        print (respone["errmsg"])
        return respone["errmsg"]
    
    def send_markdown(self,msg,user='@all'):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser" : user,
            "toparty" : self._partid,
            #"totag" : "TagID1 | TagID2",
            "msgtype" : "markdown",
            "agentid" : self._agentid,
            "markdown": {
            "content": "您的会议室已经预定，稍后会同步到`邮箱`                 >**事项详情**                 >事　项：<font color=\"info\">开会</font>                 >组织者：@miglioguan                 >参与者：@miglioguan、@kunliu、@jamdeezhou、@kanexiong、@kisonwang                 >                 >会议室：<font color=\"info\">广州TIT 1楼 301</font>                 >日　期：<font color=\"warning\">2018年5月18日</font>                 >时　间：<font color=\"comment\">上午9:00-11:00</font>                 >                 >请准时参加会议。                 >                 >如需修改会议信息，请点击：[修改会议信息](https://work.weixin.qq.com)"
            },
        #"enable_id_trans": 0,
        #"enable_duplicate_check": 0,
        #"duplicate_check_interval": 1800
        "safe":"0"
        }
        send_msges=(bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()#当返回的数据是json串的时候直接用.json即可将respone转换成字典
        print (respone["errmsg"])
        return respone["errmsg"]
        
    def send_textcard(self,msg,user='@all'):
        send_url = 'https://qyapi.weixin.qq.com/cgi-bin/message/send?access_token=' + self.get_access_token()
        send_values = {
            "touser" : user,
            "toparty" : self._partid,
            #"totag" : "TagID1 | TagID2",
            "msgtype" : "textcard",
            "agentid" : self._agentid,
            "textcard" : {
                "title" : "领奖通知",
                "description" : "<div class=\"gray\">2016年9月26日</div> <div class=\"normal\">恭喜你抽中iPhone 7一台，领奖码：xxxx</div><div class=\"highlight\">请于2016年10月10日前联系行政同事领取</div>",
                "url" : "http://119.3.254.8/todo",
                "btntxt":"更多"
            },
        #"enable_id_trans": 0,
        #"enable_duplicate_check": 0,
        #"duplicate_check_interval": 1800
        "safe":"0"
        }
        send_msges=(bytes(json.dumps(send_values), 'utf-8'))
        respone = requests.post(send_url, send_msges)
        respone = respone.json()#当返回的数据是json串的时候直接用.json即可将respone转换成字典
        print (respone["errmsg"])
        return respone["errmsg"]


if __name__ == '__main__':
    wx = WeChat_SMS()
    #wx.send_data(msg="服务崩了，你还在这里吟诗作对？")
    wx.send_textcard(msg = "")
    #以下是添加对日志的监控
    # srcfile = u"G:/123.txt"
    # file = open(srcfile)
    # file.seek(0, os.SEEK_END)
    # while 1:
    #     where = file.tell()
    #     line = file.readline()
    #     if not line:
    #         time.sleep(1)
    #         file.seek(where)
    #     else:
    #         print(line)
    #         wx.send_data(msg=line)
