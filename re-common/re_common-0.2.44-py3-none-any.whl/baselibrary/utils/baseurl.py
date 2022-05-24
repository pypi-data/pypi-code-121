import urllib.parse as parse

from re_common.baselibrary.utils.basestring import BaseString


class BaseUrl(BaseString):

    @classmethod
    def urlQuery2Dict(cls, url):
        """
        url中的参数转换成dict 字典类型方便读取
        h还有另一种 方式
        dict(parse.parse_qsl(parse.urlparse(url).query))
        :param url:
        :return:
        """
        query = parse.urlparse(url).query
        return dict([(k, v[0]) for k, v in parse.parse_qs(query).items()])

    @classmethod
    def urlPath2List(cls, url):
        """
        获取路由并返回一个列表
        :param url:
        :return:
        """
        listPath = parse.urlparse(url).path.split("/")
        try:
            listPath.remove("")
        except:
            pass
        return listPath

    @classmethod
    def urlreplaceend(cls, url, endstrins):
        list_url = url.split("/")
        list_url.pop()
        list_url.append(endstrins)
        url = "/".join(list_url)
        return url

    @classmethod
    def urlNetloc(cls, url):
        """
        获取网址
        :param url:
        :return:
        """
        return parse.urlparse(url).netloc

    @classmethod
    def urlScheme(cls, url):
        """
        获取网站的请求方式 http or https
        :param url:
        :return:
        """
        return parse.urlparse(url).scheme

    @classmethod
    def urlQuery2List(cls, url):
        """
        urllib.parse.parse_qs 返回字典
        {'CID': ['quickSearchCitationFormat'], 'database': ['1'], 'SEARCHID': ['f84e4d9aMa3f4M4e2aMae22M912f5e06a259'], 'intialSearch': ['true'], 'angularReq': ['true'], 'usageOrigin': ['searchform'], 'usageZone': ['quicksearch'], 'implicit': ['false'], 'isFullJsonResult': ['true'], 'startTime': ['1529473818439'], 'endTime': ['1529473818477']}
        urllib.parse.parse_qsl 返回列表
        [('CID', 'quickSearchCitationFormat'), ('database', '1'), ('SEARCHID', 'f84e4d9aMa3f4M4e2aMae22M912f5e06a259'), ('intialSearch', 'true'), ('angularReq', 'true'), ('usageOrigin', 'searchform'), ('usageZone', 'quicksearch'), ('implicit', 'false'), ('isFullJsonResult', 'true'), ('startTime', '1529473818439'), ('endTime', '1529473818477')]
        :param url:
        :return:
        """
        return parse.parse_qsl(parse.urlparse(url).query)

    @classmethod
    def urlQuery2dic(cls, url):
        """
        urllib.parse.parse_qs 返回字典
        {'CID': ['quickSearchCitationFormat'], 'database': ['1'], 'SEARCHID': ['f84e4d9aMa3f4M4e2aMae22M912f5e06a259'], 'intialSearch': ['true'], 'angularReq': ['true'], 'usageOrigin': ['searchform'], 'usageZone': ['quicksearch'], 'implicit': ['false'], 'isFullJsonResult': ['true'], 'startTime': ['1529473818439'], 'endTime': ['1529473818477']}
        urllib.parse.parse_qsl 返回列表
        [('CID', 'quickSearchCitationFormat'), ('database', '1'), ('SEARCHID', 'f84e4d9aMa3f4M4e2aMae22M912f5e06a259'), ('intialSearch', 'true'), ('angularReq', 'true'), ('usageOrigin', 'searchform'), ('usageZone', 'quicksearch'), ('implicit', 'false'), ('isFullJsonResult', 'true'), ('startTime', '1529473818439'), ('endTime', '1529473818477')]
        :param url:
        :return:
        """
        return parse.parse_qs(parse.urlparse(url).query)

    @classmethod
    def urlencode(cls, dic):
        """
        将dic型的url参数进行编码 如
        {'CID': 'quickSearchCitationFormat', 'database': '1', 'SEARCHID': 'f84e4d9aMa3f4M4e2aMae22M912f5e06a259', 'intialSearch': 'true', 'angularReq': 'true', 'usageOrigin': 'searchform', 'usageZone': 'quicksearch', 'implicit': 'false', 'isFullJsonResult': 'true', 'startTime': '1529473818439', 'endTime': '1529473818477'}
        :param dic:
        :return:
        """
        return parse.urlencode(dic)

    @classmethod
    def urldecode(self, strings):
        """
        url解码
        :param strings:
        :return:
        """
        return parse.unquote(strings)

    @classmethod
    def dicts_to_url(cls, dic, url=None):
        """
        将字典转换成get的url参数部分
        :param dic:
        :return:
        """
        parastring = ""
        for key, value in dic.items():
            parastring += str(key) + "=" + str(value) + "&"
        parastring = parastring[:-1]
        if url:
            return url + "?" + parastring
        return parastring

# url = "https://www.engineeringvillage.com/search/results/quick.url?CID=quickSearchCitationFormat&database=1&SEARCHID=f84e4d9aMa3f4M4e2aMae22M912f5e06a259&intialSearch=true&angularReq=true&usageOrigin=searchform&usageZone=quicksearch&implicit=false&isFullJsonResult=true&startTime=1529473818439&endTime=1529473818477"
# dic = BaseUrl.urlQuery2Dict(url)
# print(dic)
# BaseUrl.urlencode(url)
