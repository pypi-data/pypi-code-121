# coding=UTF-8
class GateWayServerConfig:
    MaxPortNum = 65536
    IP = "112.4.154.165"
    PORT = 8262
    CERTFOLDER = "./cert"
    ISTOKEN = False
    BACK_LIST = []
    backup1 = {"IP": "218.94.125.135", "Port": 8262}
    BACK_LIST.append(backup1)
    backup2 = {"IP": "221.6.24.39", "Port": 8262}
    BACK_LIST.append(backup2)
    UATIP = "168.61.2.39"
    UATPORT = 9072
    UATBACK_LIST = []
    uatbackup1 = {"IP": "168.6366.170", "Port": 9072}
    UATBACK_LIST.append(uatbackup1)
class QueryServerConfig:
     QUERY_ADDRESS = "service-insight.htsc.com.cn:9552"
     QUERY_CERT = "./cert/HTInsightCA.crt"
     QUERY_IS_SSL = True
     UATQUERY_ADDRESS = "insight-uat01.htsc.com.cn:9153"
     UATQUERY_CERT = "./cert/HTISCA.crt"
class Play_Back_Type:
    Play_Back = 0
    Play_Back_Oneday = 1


class QueryType:
    QUERY_CONSTANT = 1  # 查询历史上所有的指定证券的基础
    QUERY_CONSTANT_TODAY = 2  # 查询今日最新的指定证券的基础信息
    QUERY_ETFBASICINFO = 4 # 查询指定ETF证券的基础信息
    QUERY_TICK = 3  # 查询指定证券的最新快照信息


class SortType:
    Sort_MDTime = 0  # 0：默认方式，按照MDTime排序
    Sort_RecivedTime = 1  # 1：按照RecivedTime排序


class MDPlaybackExrightsType:
    DEFAULT_EXRIGHTS_TYPE = 0 #默认
    NO_EXRIGHTS = 1  # 不复权
    FORWARD_EXRIGHTS = 2  # 向前复权
    BACKWARD_EXRIGHTS = 3  # 向后复权


class EMarketDataType:
    UNKNOWN_DATA_TYPE = 0
    MD_TICK = 1
    MD_TRANSACTION = 2
    MD_ORDER = 3
    MD_CONSTANT = 4
    DYNAMIC_PACKET = 5
    MD_ETF_BASICINFO = 6
    MD_KLINE_1MIN = 20
    MD_KLINE_5MIN = 21
    MD_KLINE_15MIN = 22
    MD_KLINE_30MIN = 23
    MD_KLINE_60MIN = 24
    MD_KLINE_1D = 25
    MD_KLINE_15S = 26
    MD_TWAP_1MIN = 30
    MD_TWAP_1S = 31
    MD_VWAP_1MIN = 40
    MD_VWAP_1S = 41
    MD_SIMPLE_TICK = 50
    AD_UPSDOWNS_ANALYSIS = 51
    AD_INDICATORS_RANKING = 52
    AD_VOLUME_BYPRICE = 53
    AD_FUND_FLOW_ANALYSIS = 54
    AD_ORDERBOOK_SNAPSHOT = 55
    AD_ORDERBOOK_SNAPSHOT_WITH_TICK = 56
    AD_CHIP_DISTRIBUTION = 57
    MD_WARRANT = 58
    MD_SECURITY_LENDING = 59
    AD_NEWS = 60
    AD_STARING_RESULT = 61
    AD_DERIVED_ANALYSIS = 62
    MD_FI_QUOTE = 70
    MD_QUOTE = 71
    MD_QB_QUOTE = 72
    MD_QB_TRANSACTION = 73
    MD_SL_ORDER = 74
    MD_SL_TRANSACTION = 75
    MD_USA_ORDER = 76
    MD_USA_TRANSACTION = 77
    REPLAY_MD_TICK_WITH_TRANSACTION = 101
    REPLAY_MD_TICK_WITH_ORDER = 102
    REPLAY_MD_TICK_WITH_TRANSACTION_AND_ORDER = 103
    REPLAY_MD_TICK = 104
    REPLAY_MD_TRANSACTION = 105
    REPLAY_MD_ORDER = 106
    REPLAY_MD_TRANSACTION_AND_ORDER = 107


class ESubscribeActionType:
    COVERAGE = 0
    ADD = 1
    DECREASE = 2
    CANCEL = 3


class ESecurityType:
    DefaultSecurityType = 0
    IndexType = 1
    StockType = 2
    FundType = 3
    BondType = 4
    RepoType = 5
    WarrantType = 6
    OptionType = 7
    FuturesType = 8
    ForexType = 9
    RateType = 10
    NmetalType = 11
    CashBondType = 12
    SpotType = 13
    InsightType = 20
    OtherType = 99


class ESecurityIDSource:
    DefaultSecurityIDSource = 0
    XSHG = 101
    XSHE = 102
    NEEQ = 103
    XSHGFI = 104
    XSHECA = 105
    XHKG = 203
    HKSC = 204
    HGHQ = 205
    CCFX = 301
    XSGE = 302
    INE = 303
    SGEX = 401
    XCFE = 501
    CCDC = 502
    XDCE = 601
    XZCE = 602
    SWS = 701
    CNI = 702
    CSI = 703
    HTIS = 801
    MORN = 802
    QB = 803
    SPDB = 804
    HTSM = 805
    SCB = 806
    LSE = 901
    LME = 902
    LIFFE = 903
    ICEU = 904
    BSE = 905
    NSE = 906
    NEX = 907
    APEX = 908
    ICE_SG = 909
    SGX = 910
    TSE = 911
    TOCOM = 912
    OSE = 913
    EUREX = 914
    ICE = 915
    CME = 916
    CBOT = 917
    CBOE = 918
    AMEX = 919
    US = 920
    NYSE = 921
    NYMEX = 922
    COMEX = 923
    ICUS = 924
    NASDAQ = 925
    BBG = 926
    BMD = 927
    LUXSE = 928
    KRX = 929
    MICEX = 930
    ASE = 931
    ISE = 932
    DME = 933
    IHK = 934
    STOXX = 935
    SPI = 936
    NIKKEI = 937
    DJI = 938
    BATS = 939
    IEX = 940


class EPlaybackTaskStatus:
    DEFAULT_EXRIGHTS_TYPE = 0
    NO_EXRIGHTS = 10
    FORWARD_EXRIGHTS = 11
    BACKWARD_EXRIGHTS = 12
    DEFAULT_CONTROL_TYPE = 0
    CANCEL_TASK = 1
    SET_PLAYBACK_RATE = 2
    DEFAULT_STATUS = 0
    INITIALIZING = 11
    PREPARING = 12
    PREPARED = 13
    RUNNING = 14
    APPENDING = 15
    CANCELED = 16
    COMPLETED = 17
    FAILED = 18


class Error_Type:
    CONNECT_TO_SERVER_FAILED = -1000  # 连接服务器失败，网络不通
    SERVER_REJECT_LOGIN = -1001  # 服务器拒绝登录
    INVALID_MESSAGE_HANDLE = -1002  # 无效的消息处理对象，需要在登录前设置
    STREAM_SEND_ERROR = -1003  # 链路故障，发送报文失败
    STREAM_RECV_ERROR = -1004  # 链路故障，接收报文失败
    LOGIN_WAIT_TIMEOUT = -1005  # 登录超时
    INVALID_LOGIN_RESPONSE_MESSAGE = -1006  # 无效的登录应答消息，内部错误
    LOGIN_ALL_SERVERS_FAILED = -1007  # 所有服务器登录失败
    SERVICE_DISCOVERY_RESPONSE_INVALID = -1008  # 无效的服务发现应答消息
    SERVICE_DISCOVERY_RESPONSE_FAILURE = -1009  # 服务发现应答结果为：失败
    VALID_SERVER_NOT_EXIST = -1010  # 不存在可登录的服务器
    STREAM_INVALID = -1011  # 链接无效，正在重连
    SEND_WAIT_TIMEOUT_ERROR = -1012  # 请求发送超时
    RECEIVE_WAIT_TIMEOUT_ERROR = -1013  # 接收超时

    INVALID_INPUT_PORT = -1020  # 无效的输入端口号，输入检查时报告
    INVALID_INPUT_USER = -1021  # 无效的输入用户名，输入检查检测时报告
    INVALID_INPUT_IP = -1022  # 无效的ip，输入检查检测时报告
    INVALID_CLIENT = -1023  # 无效的客户端

    START_MAINTAIN_THREAD_FAILED = -2100  # 启动链接对象维护变成失败
    START_HEARTBEAT_THREAD_FAILED = -2101  # 启动心跳线程失败
    START_MESSAGE_THREAD_FAILED = -2102  # 启动消息处理线程失败
    START_HANDLE_THREAD_FAILED = -2103  # 启动handle处理线程失败
    STOP_LOGIN_FOR_QUIT = -2104  # 客户端退出，停止登录
    ACQUIRE_QUIT_MUTEX_FAILED = -2105  # 请求锁失败，内部错误
    GET_MESSAGE_FROM_QUEUE_TIMEOUT = -2106  # 获取消息超时
    SUBSCRIBE_RESPONSE_REJECT = -2107  # 订阅应答结果为拒绝
    SUBSCRIBE_RESPONSE_HEADER_ID_NOT_EQUAL = -2108  # 订阅应答消息头不一致，错位的订阅应答，丢弃
    INVALID_EMDC_MESSAGE_TYPE = -2109  # 无效的EMDC消息类型
    INVALID_PACKAGE_SIZE = -2110  # 无效的包长度
    NULL_MESSAGE_POINTER = -2111  # 消息指针为NULL，内部异常
    INVALID_INSIGHT_MESSAGE_HEADER = -2112  # 无效的消息头
    INVALID_INSIGHT_MESSAGE_BODY = -2113  # 无效的消息体
    SERIALIZE_MESSAGE_HEADER_TO_ARRAY_FAILED = -2114  # 序列化消息头失败
    SERIALIZE_MESSAGE_BODY_TO_ARRAY_FAILED = -2115  # 序列化消息体失败
    PARSE_MESSAGE_HEADER_FROM_ARRAY_FAILED = -2116  # 从数组中解析消息头失败
    PARSE_MESSAGE_BODY_FROM_ARRAY_FAILED = -2117  # 从数组中解析消息体失败
    INVALID_INSIGHT_MESSAGE_BUF = -2118  # 无效的消息缓冲
    OUT_OF_MEMORY = -2120  # 内存不足
    INVALID_SUBSCRIBE_INPUT = -2121  # 无效的订阅输入
    SUBSCRIBE_FAILED = -2122  # 订阅失败
    CLIENT_IS_ALREADY_LOGIN = -2300  # 已登录不能重复登录
    WAIT_SUBSCRIBE_RESPONSE_TIMEOUT = -2301  # 等待订阅应答超时
    INVALID_MDQUERY_RESPONSE_MESSAGE = -2302  # 无效的查询应答消息
    WAIT_PLAYBACK_RESPONSE_TIMEOUT = -2303  # 等待回放应答超时
    WAIT_MDQUERY_RESPONSE_TIMEOUT = -2304  # 等待查询应答失败
    PLAYBACK_RESPONSE_REJECT = -2305  # 回放应答结果为：拒绝
    MDQUERY_RESPONSE_ERROR = -2306  # 查询应答错误
    MDQUERY_RESPONSE_FAILURE = -2307  # 查询结果为失败
    ACQUIRE_SUBSCRIBE_MUTEX_FAILED = -2308  # 请求订阅锁失败，内部错误
    INVALID_SUBSCRIBE_MESSAGE_BODY = -2309  # 订阅消息体无效

    INIT_SSL_CONTEXT_FAILED = -2400  # 初始化SSL环境错误
    SSL_VERIFY_PRIVATE_KEY_FAILED = -2401  # SSL验证key失败
    PLAYBACK_CONTROL_RESPONSE_REJECT = -2402  # 回放控制应答结果为：拒绝
    QUERY_RESPONSE_CITATION_REJECT = -2403  # 选择回调函数处理查询回复，却使用引用返回回复
    QUERY_RESPONSE_CALLBACK_REJECT = -2404  # 未选择回调函数处理查询回复，却未使用应用返回回复

    UNKNOWN_PROPERTY_NAME = -2501  # 未知的参数名


class ErrorInfo:
    @staticmethod
    def get_error_code_value(code):
        value = "未知错误类型"
        if code == Error_Type.CONNECT_TO_SERVER_FAILED:
            value = "连接服务器失败，网络不通"
        if code == Error_Type.SERVER_REJECT_LOGIN:
            value = "服务器拒绝登录"
        if code == Error_Type.INVALID_MESSAGE_HANDLE:
            value = "无效的消息处理对象，需要在登录前设置"
        if code == Error_Type.STREAM_SEND_ERROR:
            value = "链路故障，发送报文失败"
        if code == Error_Type.STREAM_RECV_ERROR:
            value = "链路故障，接收报文失败"
        if code == Error_Type.LOGIN_WAIT_TIMEOUT:
            value = "登录超时"
        if code == Error_Type.INVALID_LOGIN_RESPONSE_MESSAGE:
            value = "无效的登录应答消息，内部错误"
        if code == Error_Type.LOGIN_ALL_SERVERS_FAILED:
            value = "所有服务器登录失败"
        if code == Error_Type.SERVICE_DISCOVERY_RESPONSE_INVALID:
            value = "无效的服务发现应答消息"
        if code == Error_Type.SERVICE_DISCOVERY_RESPONSE_FAILURE:
            value = "服务发现应答结果为：失败"
        if code == Error_Type.VALID_SERVER_NOT_EXIST:
            value = "不存在可登录的服务器"
        if code == Error_Type.STREAM_INVALID:
            value = "链接无效，正在重连"
        if code == Error_Type.SEND_WAIT_TIMEOUT_ERROR:
            value = "请求发送超时"
        if code == Error_Type.RECEIVE_WAIT_TIMEOUT_ERROR:
            value = "接收超时"
        if code == Error_Type.INVALID_INPUT_PORT:
            value = "无效的输入端口号，输入检查时报告"
        if code == Error_Type.INVALID_INPUT_USER:
            value = "无效的输入用户名，输入检查检测时报告"
        if code == Error_Type.INVALID_INPUT_IP:
            value = "无效的ip，输入检查检测时报告"
        if code == Error_Type.START_MAINTAIN_THREAD_FAILED:
            value = "启动链接对象维护变成失败"
        if code == Error_Type.START_HEARTBEAT_THREAD_FAILED:
            value = "启动心跳线程失败"
        if code == Error_Type.START_MESSAGE_THREAD_FAILED:
            value = "启动消息处理线程失败"
        if code == Error_Type.START_HANDLE_THREAD_FAILED:
            value = "启动handle处理线程失败"
        if code == Error_Type.STOP_LOGIN_FOR_QUIT:
            value = "客户端退出，停止登录"
        if code == Error_Type.ACQUIRE_QUIT_MUTEX_FAILED:
            value = "请求锁失败，内部错误"
        if code == Error_Type.GET_MESSAGE_FROM_QUEUE_TIMEOUT:
            value = "获取消息超时"
        if code == Error_Type.SUBSCRIBE_RESPONSE_REJECT:
            value = "订阅应答结果为拒绝"
        if code == Error_Type.SUBSCRIBE_RESPONSE_HEADER_ID_NOT_EQUAL:
            value = "订阅应答消息头不一致，错位的订阅应答，丢弃"
        if code == Error_Type.INVALID_EMDC_MESSAGE_TYPE:
            value = "无效的EMDC消息类型"
        if code == Error_Type.INVALID_PACKAGE_SIZE:
            value = "无效的包长度"
        if code == Error_Type.NULL_MESSAGE_POINTER:
            value = "消息指针为NULL，内部异常"
        if code == Error_Type.INVALID_INSIGHT_MESSAGE_HEADER:
            value = "无效的消息头"
        if code == Error_Type.INVALID_INSIGHT_MESSAGE_BODY:
            value = "无效的消息体 "
        if code == Error_Type.SERIALIZE_MESSAGE_HEADER_TO_ARRAY_FAILED:
            value = "序列化消息头失败"
        if code == Error_Type.SERIALIZE_MESSAGE_BODY_TO_ARRAY_FAILED:
            value = "序列化消息体失败"
        if code == Error_Type.PARSE_MESSAGE_HEADER_FROM_ARRAY_FAILED:
            value = "从数组中解析消息头失败"
        if code == Error_Type.PARSE_MESSAGE_BODY_FROM_ARRAY_FAILED:
            value = "从数组中解析消息体失败"
        if code == Error_Type.INVALID_INSIGHT_MESSAGE_BUF:
            value = "无效的消息缓冲"
        if code == Error_Type.OUT_OF_MEMORY:
            value = "内存不足"
        if code == Error_Type.INVALID_SUBSCRIBE_INPUT:
            value = "无效的订阅输入"
        if code == Error_Type.SUBSCRIBE_FAILED:
            value = "订阅失败"
        if code == Error_Type.CLIENT_IS_ALREADY_LOGIN:
            value = "已登录不能重复登录"
        if code == Error_Type.WAIT_SUBSCRIBE_RESPONSE_TIMEOUT:
            value = "等待订阅应答超时"
        if code == Error_Type.INVALID_MDQUERY_RESPONSE_MESSAGE:
            value = "无效的查询应答消息"
        if code == Error_Type.WAIT_PLAYBACK_RESPONSE_TIMEOUT:
            value = "等待回放应答超时"
        if code == Error_Type.WAIT_MDQUERY_RESPONSE_TIMEOUT:
            value = "等待查询应答失败"
        if code == Error_Type.PLAYBACK_RESPONSE_REJECT:
            value = "回放应答结果为：拒绝"
        if code == Error_Type.MDQUERY_RESPONSE_ERROR:
            value = "查询应答错误"
        if code == Error_Type.MDQUERY_RESPONSE_FAILURE:
            value = "查询结果为失败"
        if code == Error_Type.ACQUIRE_SUBSCRIBE_MUTEX_FAILED:
            value = "请求订阅锁失败，内部错误"
        if code == Error_Type.INVALID_SUBSCRIBE_MESSAGE_BODY:
            value = "订阅消息体无效"
        if code == Error_Type.INIT_SSL_CONTEXT_FAILED:
            value = "初始化SSL环境错误"
        if code == Error_Type.SSL_VERIFY_PRIVATE_KEY_FAILED:
            value = "SSL验证key失败"
        if code == Error_Type.PLAYBACK_CONTROL_RESPONSE_REJECT:
            value = "回放控制应答结果为：拒绝"
        if code == Error_Type.QUERY_RESPONSE_CITATION_REJECT:
            value = "选择回调函数处理查询回复，却使用引用返回回复"
        if code == Error_Type.QUERY_RESPONSE_CALLBACK_REJECT:
            value = "未选择回调函数处理查询回复，却未使用应用返回回复"
        if code == Error_Type.UNKNOWN_PROPERTY_NAME:
            value = "未知的参数名"
        else:
            value = "未知错误类型"
        return value
