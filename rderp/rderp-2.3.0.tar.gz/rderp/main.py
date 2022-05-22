from k3cloud_webapi_sdk.main import K3CloudApiSdk
class ErpClient(K3CloudApiSdk):
    def __init__(self,acct_id,user_name,app_id,app_secret,server_url,token="AD64F20D-6063-4E87-81E8-A24C1751D758",timeout=120):
        K3CloudApiSdk.__init__(self)
        self.acct_id = acct_id
        self.user_name = user_name
        self.app_id = app_id
        self.app_secret = app_secret
        self.server_url = server_url
        self.timeout = timeout
        K3CloudApiSdk.InitConfig(self,acct_id=self.acct_id, user_name=self.user_name, app_id=self.app_id,
                           app_secret=self.app_secret, server_url=self.server_url)

if __name__ == '__main__':
    app = ErpClient(acct_id='606ada0b30a9e2', user_name='胡立磊', app_id='224986_TY8p2yGs4vg9Xf0tRfSA3a/N6K3d6OlH',
                       app_secret='e1e0cdc4e8204d178cc383557e64e959', server_url='http://8.133.163.217/k3cloud/')
    print(app.View("BD_MATERIAL", {
        "CreateOrgId": 0,
        "Number": "02.01.010",
        "Id": ""
    }))

