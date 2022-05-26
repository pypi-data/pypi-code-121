# URL为何要编码、解码？
#
#     通常如果一样东西需要编码，说明这样东西并不适合传输。原因多种多样，如Size过大，包含隐私数据。对于Url来说，之所以要进行编码，是因为Url中有些字符会引起歧义。
#
#     例如，Url参数字符串中使用key=value键值对这样的形式来传参，键值对之间以&符号分隔，如/s?q=abc&ie=utf-8。如果你的value字符串中包含了=或者&，那么势必会造成接收Url的服务器解析错误，因此必须将引起歧义的&和=符号进行转义，也就是对其进行编码。
#
#     又如，Url的编码格式采用的是ASCII码，而不是Unicode，这也就是说你不能在Url中包含任何非ASCII字符，例如中文。否则如果客户端浏览器和服务端浏览器支持的字符集不同的情况下，中文可能会造成问题。
# -*- coding: utf-8 -*-

from urllib.request import quote, unquote

from sometools.sync_tools.base import Base


class UrlEncodeDecodeMixIn(Base):
    def __init__(self, *args, **kwargs):
        super(UrlEncodeDecodeMixIn, self).__init__(*args, **kwargs)

    @staticmethod
    def url_encode(url: str, encoding: str = "utf-8") -> str:
        # 编码
        # utf8编码，指定安全字符
        ret = quote(url, safe=";/?:@&=+$,", encoding="utf-8")
        return ret
        # gbk编码
        # ret2 = quote(url1, encoding="gbk")

    @staticmethod
    def url_decode(url: str, encoding: str = "utf-8") -> str:
        # 编码
        # utf8编码，指定安全字符
        ret = unquote(url, encoding='utf-8')
        return ret


if __name__ == '__main__':
    print(UrlEncodeDecodeMixIn().url_encode('https://www.baidu.com/s?wd=中国'))
    print(UrlEncodeDecodeMixIn().url_decode('https://www.baidu.com/s?wd=%E4%B8%AD%E5%9B%BD'))


