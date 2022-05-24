USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.106 Safari/537.36'

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.62 Safari/537.36",
    "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
    "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
    "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
    "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 2.0.50727; Media Center PC 6.0)",
    "Mozilla/5.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0; WOW64; Trident/4.0; SLCC2; .NET CLR 2.0.50727; .NET CLR 3.5.30729; .NET CLR 3.0.30729; .NET CLR 1.0.3705; .NET CLR 1.1.4322)",
    "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
    "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
    "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
    "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
    "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
    "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52",
]

INSIDE_HEADERS = {
    "accept": "application/json",
    "content-type": "application/json"
}


def set_proxy(proxy):
    Proxiesss = {
        'http': proxy,
        'https': proxy
    }
    return Proxiesss


def set_proxy_aio(proxy):
    if proxy:
        return r"http://" + proxy
    return None


def set_proxy_httpx(proxy):
    if proxy:
        Proxiesss = {
            'http://': "http://" + proxy,
            'https://': "http://" + proxy
        }
        return Proxiesss
    else:
        return None


class MsgCode(object):
    SUCCESS_CODE: int = 200  # 成功状态码

    NO_RESOURCE: int = 421  # 网页明确表明无资源
    PAGE_BLANK: int = 420  # 网页空白页
    END_STRING_ERROR: int = 210  # html结尾验证错误
    MARK_ERROR: int = 211  # 验证html错误，验证没有通过
    NOT_IS_JSON: int = 212  # 验证返回是否是json
    VER_CODE: int = 213  # 需要验证码
    NONE_HTML: int = 214  # html为空 空的html 在使用某些代理时 如果https 写成了http,会有这种情况
    STATUS_ERROR: int = 215  # API接口内部执行错误
    CODE_ERROR: int = 216  # data 状态码错误
    URL_TIMEOUT: int = 217

    SETTING_CONFIG_ERROR: int = 251 # 特定错误 更新taskinfo_save_setting的任务控制配置失败(switch参数错误,只能为0或1)

    API_FAIL_CODE: int = 400  # api失败，但具体原因未知的状态码
    TIME_OUT_ERROR: int = 408  # 超时错误
    PROXY_ERROR: int = 422  # 代理错误
    PAYLOAD_ERROR: int = 423  # 非法的压缩格式，错误的chunk编码，数据不足Content-length的大小。通常为Accept-Encoding:gzip, deflate, br ，也就是三种编码格式。但其实，aiohttp默认没有br解码，或者html编码格式错误
    SERVER_ERROR: int = 530  # 服务器异常错误，被捕获发送
    CHAOXIN_COOKIE_ERROR: int = 556  # 超星期刊获取cookie失败

    DATABASE_CONFIG_IN_CODE: int = 998  # 在代码中配置数据库无对应错误码

    ON_KNOW: int = 1000  # 未知错误

    MONGO_ERROR: int = 1001  # mongodb 錯誤系列由1000 到 1100
    MONGO_NO_ID: int = 1002  # 操作时由于没有该id的状态码，比如更新时ID不存在

    PARE_STRUCTURE_ERROR: int = 1101  # 解析系列由1100 到 1200，解析结构错误
    PARE_NO_DATA: int = 1102  # 没有数据，且认为是正常的没有数据的标识
    PARE_NO_DATA_ERR: int = 1103  # 没有数据，且认为是非正常的没有数据的标识
    SQL_INSERT_ERROR: int = 1201  # sql错误 由 1200 到 1300 insert 错误
    SQL_UPDATE_ERROR: int = 1202  # update 错误
    SQL_SELECT_ALL_ERROR: int = 1203  # 执行fetchall 错误
    SQL_EXECUTEMANY_ERROR: int = 1204  # executemany 执行错误
    SQL_EXECUTE_ERROR: int = 1205  # execute 执行错误
    SQL_REPLACE_ERROR: int = 1206  # replace 执行错误

    GRPC_MESSAGE_DECODEERROR: int = 1301  # grpc服务编码错误


SUCCESS = "SUCCESS"
FAILED = "FAILED"
