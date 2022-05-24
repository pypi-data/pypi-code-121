import json

import requests

from re_common.baselibrary.utils.baserequest import BaseRequest


class WorkWechatBot(object):

    def __init__(self,key):
        super().__init__()
        self.bsrequest = BaseRequest()
        self.upurl = "https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={}&type=file".format(key)
        self.url = "https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={}".format(key)

    def sendMsg(self, data):
        headers = {"Content-Type": "application/json"}
        BoolResult, errString, r = self.bsrequest.base_request_post(self.url,
                                                                    headers=headers,
                                                                    data=data,
                                                                    timeout=(10, 30)
                                                                    )
        if BoolResult:
            dicts = json.loads(r.text)
            if dicts["errcode"] == 0:
                return True,dicts
            else:
                return False,dicts
        else:
            return False, errString

    def uploadFile(self, files):
        headers = {
            "Content-Type": "multipart/form-data;"
        }
        r = requests.post(self.url, files=files, headers=headers)
        # BoolResult, errString, r = self.bsrequest.base_request_post(self.url,
        #                                                             headers=headers,
        #                                                             files=upfile,
        #                                                             timeout=(10, 30)
        #                                                             )
        print(r.text)

    def sendTextMsg(self,msg,options=None):
        data = {
            "msgtype": "text",
            "text": {
                "content": msg
             }
        }
        if options:
            data["text"] .update(options)
        return self.sendMsg(data)

    def sendMarkDownMsg(self,msg,options=None):
        data = {
            "msgtype": "markdown",
            "markdown": {
                "content": msg
             }
        }
        if options:
            data["text"] .update(options)
        return self.sendMsg(data)

    def sendImage(self, msg):
        data = {
            "msgtype": "image",
            "image": msg
        }
        return self.sendMsg(data)

    def sendTxtImage(self, msg):
        data = {
            "msgtype": "news",
            "articles": msg
        }
        return self.sendMsg(data)

if __name__ == "__main__":
    wxb = WorkWechatBot("5a822419-b7b2-4036-a136-5e75f028ddfb")
    #wxb.sendTextMsg("额...")
    files = {'file': ('test.txt',open(r'E:\test.txt', 'rb'),"media")}
    wxb.uploadFile(files)
