from requests import  *
class Client:
    def __init__(self,name='client', endPoint="http://58.211.213.34:88/test", authcode="3BBf3C56", username='admin'):
        self.name = name
        self.endPoint = endPoint
        self.authcode = authcode
        self.username = username
        self.url_key = self.endPoint + "/crmapi/apiKey.php"
        self.data = {'authen_code': self.authcode}
        r = post(url=self.url_key, data=self.data)
        res = r.json()
        self.info = res
        self.code = res['code']
        self.key = res['key']
        self.token = res['token']
    def __str__(self):
        return(self.name)

    def save(self, data,url):
        if self.code == 'success':
            data['apikey'] = self.key
            data['token'] = self.token
            data['username'] = self.username
            url_product = self.endPoint + url
            r_prd = post(url=url_product, data=data)
        return (r_prd.json())
    def query(self,module,fieldname,fieldvalue,url):
        if self.code == 'success':
            searchtext = [{
                'groupid': '1',
                'module': module,
                'fieldname': fieldname,
                'comparator': '包含',
                'value': fieldvalue,
                'columncondition': '',
                'groupcondition': ''
            }]
            data = {
                "module": module,
                "func": "getList",
                'apikey': self.key,
                'token': self.token,
                'username': self.username,
                'searchtext': searchtext
            }
            url_query = self.endPoint + url
            r = post(url=url_query, json=data)
            res = r.json()
            return(res)


if __name__ =='__main__':
    app = Client()
    print(app)
    print(app.info)
    print(app.code)
    print(app.key)
    print(app.token)

