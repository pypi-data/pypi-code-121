import json
import requests
import time


######################################################################

class YDMHttp(object):
    """
    云打码已废弃，（跑路）
    """

    def __init__(self, username='office', password='officeHelper$123', appid=1, appkey='22cc5376925e9387a23cf797cb9ba745'):
        self.username = username
        self.password = password
        self.appid = str(appid)
        self.appkey = appkey
        self.apiurl = 'http://api.yundama.com/api.php'

    def request(self, fields, files=[]):
        response = self.post_url(self.apiurl, fields, files)
        response = json.loads(response)
        return response

    def balance(self):
        data = {'method': 'balance', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['balance']
        else:
            return -9001

    def login(self):
        data = {'method': 'login', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey}
        response = self.request(data)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['uid']
        else:
            return -9001

    def upload(self, filename, codetype, timeout):
        data = {'method': 'upload', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'codetype': str(codetype), 'timeout': str(timeout)}
        file = {'file': filename}
        response = self.request(data, file)
        if (response):
            if (response['ret'] and response['ret'] < 0):
                return response['ret']
            else:
                return response['cid']
        else:
            return -9001

    def result(self, cid):
        data = {'method': 'result', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid)}
        response = self.request(data)
        return response and response['text'] or ''

    def decode(self, filename, codetype, timeout):
        cid = self.upload(filename, codetype, timeout)
        if (cid > 0):
            for i in range(0, timeout):
                result = self.result(cid)
                if (result != ''):
                    return cid, result
                else:
                    time.sleep(1)
            return -3003, ''
        else:
            return cid, ''

    def report(self, cid):
        data = {'method': 'report', 'username': self.username, 'password': self.password, 'appid': self.appid,
                'appkey': self.appkey, 'cid': str(cid), 'flag': '0'}
        response = self.request(data)
        if (response):
            return response['ret']
        else:
            return -9001

    def post_url(self, url, fields, files=[]):
        #  在传入二进制时，下面两行官方代码需注释掉
        # for key in files:
        #     files[key] = open(files[key], 'rb');
        res = requests.post(url, files=files, data=fields)
        return res.text


######################################################################

    def Img2Code(self, content, codetype='1004', timeout=5):
        """

        :param content: 图片文件
        :param codetype: 验证码类型,
        例：1004表示4位字母数字，不同类型收费不同。请准确填写，否则影响识别率。
            在此查询所有类型 http://www.yundama.com/price.html
        :param timeout: 超时时间，秒
        :return: 验证码
        """

        # 登陆云打码
        uid = self.login()
        print('uid: %s' % uid)

        # 查询余额
        balance = self.balance()
        print('balance: %s' % balance)
        if int(balance) < 100000:
            print('Warning: Need Money !!!!!!!!!!!!!!!!!!!!!!!!!')

        # 开始识别，图片路径，验证码类型ID，超时时间（秒），识别结果
        cid, result = self.decode(content, codetype, timeout)
        print('cid: %s, result: %s' % (cid, result))
        return result


