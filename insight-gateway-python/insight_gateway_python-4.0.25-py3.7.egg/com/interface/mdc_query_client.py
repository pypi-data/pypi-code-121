import os,sys
sys.path.insert(1, "./model")
from Crypto.Cipher import AES
from binascii import b2a_hex
import grpc
from model import IInsightQueryService_pb2 as IInsightQueryService_pb2
from model import MDSignOnService_pb2 as MDSignOnService_pb2
from model import MDSignOnService_pb2_grpc as MDSignOnService_pb2_grpc, \
    IInsightQueryService_pb2_grpc as IInsightQueryService_pb2_grpc
import logging
import threading


class MdcQueryClient(object):
    _instance_lock = threading.Lock()

    def __init__(self, root_cert,open_file_log,open_cout_log):
        self.root_cert = root_cert
        self.file_log = open_file_log
        self.cout_log = open_cout_log
        self.read_root_cert(root_cert)
        self.timeout = 180
        self.__init_log__();

    def __init_log__(self):
        self.thread_id = str(threading.currentThread().ident)
        handlers = []
        fp = logging.FileHandler('query_' + self.thread_id + '.log', encoding='utf-8')
        fs = logging.StreamHandler()
        if self.file_log:
            handlers.append(fp)
        if self.cout_log:
            handlers.append(fs)
        logging.basicConfig(level=logging.DEBUG,
                            format="%(asctime)s000 pid[" + self.thread_id + "] %(levelname)s  %(message)s",
                            handlers=handlers)  # 调用
        logging.basicConfig(level=logging.ERROR,
                            format="%(asctime)s000 pid[" + self.thread_id + "] %(levelname)s  %(message)s",
                            handlers=handlers)
        logging.basicConfig(level=logging.WARNING,
                            format="%(asctime)s000 pid[" + self.thread_id + "] %(levelname)s  %(message)s",
                            handlers=handlers)
        logging.basicConfig(level=logging.INFO,
                            format="%(asctime)s000 pid[" + self.thread_id + "] %(levelname)s  %(message)s",
                            handlers=handlers)

    def __new__(cls, *args, **kwargs):
        if not hasattr(MdcQueryClient, "_instance"):
            with MdcQueryClient._instance_lock:
                if not hasattr(MdcQueryClient, "_instance"):
                    MdcQueryClient._instance = object.__new__(cls)
        return MdcQueryClient._instance

    def set_timeout_sec(self, timeout):
        self.timeout = timeout
        pass

    def channel_init(self, username, password, url):
        self.username = username
        self.password = password
        self.url = url
        creds = grpc.ssl_channel_credentials(self.read_root_cert(self.root_cert), None, None)
        self.channel = grpc.secure_channel(self.url, creds)

    def token_init(self):
        stubSign = MDSignOnService_pb2_grpc.MDSignOnServiceStub(self.channel)
        signRequest = MDSignOnService_pb2.MDSignOnQueries.MDSignOnRequest()
        signRequest.username = (self.username)
        signRequest.password = self.encode(self.password)
        responseSign = stubSign.getTokenByAccountInfo(signRequest)
        if responseSign.IsSuccess:
            self.token = str(responseSign.token)
            logging.info(self.token)
        else:
            logging.error(responseSign.InsightErrorContext)
            exit(0)

    def login_by_password(self, username, password, url):
        self.channel_init(username, password, url)
        self.token_init()

    def request_query(self, appType, queryType, queryParams, htscSecurityIDs, securitySourceType):
        queryRequest = IInsightQueryService_pb2.InsightQueryRequest()
        # 用户账户
        queryRequest.userAccount = self.username
        # 用户认证令牌
        queryRequest.userToken = self.token
        # 用户应用类别
        queryRequest.appType = appType
        queryRequest.queryType = queryType
        for key in queryParams:
            queryRequest.queryParams[key] = queryParams[key]
        if htscSecurityIDs is not None:
            for htscSecurityID in htscSecurityIDs:
                queryRequest.htscSecurityIDs.append(htscSecurityID)
        if securitySourceType is not None:
            queryRequest.securitySourceType = securitySourceType

        responseList = []
        stub = IInsightQueryService_pb2_grpc.IInsightQueryServiceStub(self.channel)
        for response in stub.accessInsightQuery(queryRequest, self.timeout):
            if response.errorContext.errorCode == 401401:
                logging.error(">>>>>>> %s, token %s is error " % ( str(response), self.token))
                self.token_init()
                logging.info(">>>>>>> the new token is %s" % self.token)
                return self.request_query(appType, queryType, queryParams, htscSecurityIDs, securitySourceType)
            else:
                responseList.append(response)
        return responseList

    def read_root_cert(self, root_folder):
        with open(root_folder + 'HTISCA.crt', 'rb') as f:
            root_certificates = f.read()
        return root_certificates

    def get_token(self):
        return self.token

    def add_to_16(self,s):
        while len(s) % 16 != 0:
            s += (16 - len(s) % 16) * chr(16 - len(s) % 16)
        return str.encode(s)  # 返回bytes

    def encode(self, text):  # 待加密文本
        key = 'insight_9_mdcp_6'  # 密钥长度必须为16、24或32位，分别对应AES-128、AES-192和AES-256
        aes = AES.new(str.encode(key), AES.MODE_ECB)  # 初始化加密器，本例采用ECB加密模式
        value = self.add_to_16(text)
        code = aes.encrypt(value)
        return b2a_hex(code)