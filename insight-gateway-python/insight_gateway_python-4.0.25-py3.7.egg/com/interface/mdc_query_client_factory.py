from __future__ import print_function
from com.interface.mdc_query_client import MdcQueryClient

class MdcQueryClientFactory:
    def get_instance(self):
        return self.mdcQueryClient

    def create_query_client(self, cert_folder,open_file_log,open_cout_log):
        self.mdcQueryClient = MdcQueryClient(cert_folder,open_file_log,open_cout_log)
        return self.mdcQueryClient

# 资讯因子等查询接口-----该接口查询结果以JSON形式直接返回，相关参数请查阅数据手册
class DerviteQuery():
    def __init__(self):
        self.factory = MdcQueryClientFactory()

    def init(self,open_file_log,open_cout_log):
        self.factory.create_query_client("./cert/", open_file_log, open_cout_log)
        self.client = self.factory.get_instance()

    def query_derivate_login(self,usr,pwd,url,timeout=10):
        self.client.login_by_password(usr, pwd, url)
        self.client.set_timeout_sec(timeout)

    def query_derivate(self,queryType,queryParams,htscSecurityIDs,securitySourceType):
        try:
            appType = "101"
            request = self.client.request_query(appType, queryType, queryParams, htscSecurityIDs, securitySourceType)
        except BaseException as e:
            print("error happended in query_derivate")
            print(e)
        return request