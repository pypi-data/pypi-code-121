# -*- coding: utf-8 -*-
'''
@Time    : 2022/5/18 11:57 AM
@Author  : oujiewen2@shoplineapp.com
@File    : loginHelper.py
登录流程
'''
import requests as s
import json
class loginHelper:
    def __init__(self,parmas):
        self.parmas=parmas

    def login_main(self,user,userName):
        '''
        登录的4个接口，一团乱麻不想整理
                {"oujiewen2+xiaohei@shoplineapp.com":{"pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5",
                                                     "handel":"interface-automation",
                                                     "cookiesName":"小黑"}，
                "oujiewen2+0001@shoplineapp.com":{"pwd":"9baca9a3b4cb6a6195fe559c118d8bcd2f5e9a398a1c486cb571d7cc6f6ae26257e4dda78f85ce1c86f09408d93fb1c5cb830870f45c4c5c51e16528d89545573d41028bdc42290f500ae681a074e31da00b81f29f846f611efd6b182cf8058a4a264ef0e4ef1ee4046fca6ca66283d972173f6a969f5b6cb428564b3b6b94c5",
                                                "handel":"interface-automation",
                                                "cookiesName":"店长"}
                }
        '''
        # 保存的cookie的名称
        cookies_name = user['cookiesName']
        my_session = s.session()
        # 获取stoken
        stoken_url = self.parmas['host'] + "/udb/lgn/login/init.do?subappid=1&appid=" + self.parmas[
            'appid'] + "&callback=js&lang=zh-hans-cn&type=email"
        stoken = my_session.request('get', stoken_url).json()['stoken']
        # 登录verify接口
        # verify.do入参
        verify_params = {
            "method": "get",
            "url": self.parmas["host"] + '/udb/lgn/login/verify.do',
            "params": {
                "subappid": 1,
                "appid": self.parmas['appid'],
                "callback": "js",
                "lang": "zh-hans-cn",
                "acct": userName,
                "pwd": user['pwd'],
                "stoken": stoken
            }
        }
        my_session.request(**verify_params)
        # 获取a_mach
        url_s = self.parmas['handel'] + "/admin/api/merchant/merchants/" + user['handel'] + "/enter?enterType=0"
        a_mach = my_session.post(url=url_s).json()['data']
        # print(a_mach)
        # 把a_mach加入cookie
        my_session.cookies['a_mach'] = a_mach
        # print(my_session.cookies)
        # 把cookie转字典
        my_cookies_dict = s.utils.dict_from_cookiejar(my_session.cookies)

        # 获取contextToken，并替换a_ste的值
        contextToken = my_session.request("get", self.parmas['handel'] + "/admin/api/merchant/stores/" + user[
            'handel'] + "/enter?enterType=1").json()['data']['contextToken']
        my_cookies_dict['a_ste'] = contextToken

        # 把cookie转成字符串
        cookies_str = ''
        for key in my_cookies_dict:
            cookies_str = cookies_str + str(key) + '=' + str(my_cookies_dict[key]) + ';'
        self.parmas[cookies_name] = cookies_str
        print(self.parmas[cookies_name])
        return self.parmas