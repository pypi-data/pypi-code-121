import json
import zlib

import aiofiles
import aiohttp
from yarl import URL


class BaseAiohttp():

    def __init__(self):
        self.session = aiohttp.ClientSession()
        # 用于传递get的参数
        # params = {'key1': 'value1', 'key2': 'value2'}
        # params = [('key', 'value1'), ('key', 'value2')] 同建多值问题
        # params='key=value+1' 您也可以将str内容作为参数传递，但要注意–内容不是由库编码的。
        # 请注意，+未编码
        self.params = {}
        # post json
        self.json = {}
        # post表单数据 {'key1': 'value1', 'key2': 'value2'}
        self.payload = {}
        # 如果您要发送未经格式编码的数据，可以通过传递a bytes而不是a来完成dict。
        # 这些数据将直接发布，并且默认将内容类型设置为“ application / octet-stream”：
        # =b'\x00Binary-data\x00'
        # 要发送具有适当内容类型的文本，只需使用text属性 data='Тест'
        # 要上传多部分编码的文件，请执行以下操作：
        # files = {'file': open('report.xls', 'rb')}
        # 您可以设置filename和content_type：
        # data = FormData()
        # data.add_field('file',
        #                open('report.xls', 'rb'),
        #                filename='report.xls',
        #                content_type='application/vnd.ms-excel')
        # 如果将文件对象作为数据参数传递，则aiohttp会将其自动流式传输到服务器。
        # 检查StreamReader 支持的格式信息。
        self.data = b''
        # headers可以是单个请求的，也可以是会话的
        self.headers = {}
        # {'cookies_are': 'working'}
        self.cookies = {}

    async def file_sender(self, file_name=None, size=64):
        """
        async with session.post('http://httpbin.org/post',
                        data=file_sender(file_name='huge_file')) as resp:
            print(await resp.text())
        :param file_name:
        :param size:
        :return:
        """
        async with aiofiles.open(file_name, 'rb') as f:
            chunk = await f.read(size * 1024)
            while chunk:
                yield chunk
                chunk = await f.read(size * 1024)

    def get_and_send(self):
        """
        从版本3.1开始不推荐使用：aiohttp仍然支持aiohttp.streamer装饰器，
        但是不推荐使用此方法，而支持异步生成器，如上所示。
        Python 3.5没有对异步生成器的本机支持，请使用 async_generator库作为解决方法。
        因为该content属性是 StreamReader（提供异步迭代器协议），所以您可以将获取和发布请求链接在一起：
        resp = await session.get('http://python.org')
        await session.post('http://httpbin.org/post',
                           data=resp.content)
        :return:
        """
        pass

    def web_sockets(self, url):
        """

        :return:
        """
        async with self.session.ws_connect(url) as ws:
            async for msg in ws:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    if msg.data == 'close cmd':
                        await ws.close()
                        break
                    else:
                        await ws.send_str(msg.data + '/answer')
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    break

    def data_upfile(self, file):
        """

        :param file:
        :return:
        """
        with open(file, 'rb') as f:
            await self.session.post('http://httpbin.org/post', data=f)

    def init_session(self, json_serialize=json.dumps, headers=None,
                     cookies=None, cookie_jar=None, connector=None):
        """

        :param json_serialize: 默认使用json.dumps 这里可以使用 ujson.dumps
        ujson库比标准库快，json但是有点不兼容。
        :param headers:
        :param cookies:
        :param cookie_jar:默认情况下ClientSession使用的严格版本 aiohttp.CookieJar。RFC 2109明确禁止cookie接受具有IP地址而不是DNS名称的URL（例如 http://127.0.0.1:80/cookie）。
        很好，但有时为了进行测试，我们需要启用对此类Cookie的支持。应该通过将unsafe = True传递给 aiohttp.CookieJar构造函数来完成：
        jar = aiohttp.CookieJar(unsafe=True)
        jar = aiohttp.DummyCookieJar()
        :return:
        """

        self.session = aiohttp.ClientSession(json_serialize=json_serialize, headers=headers,
                                             cookies=cookies, cookie_jar=cookie_jar,
                                             connector=connector)

    def deflate_zip(self, data, headers):
        """

        :return:
        """
        headers['Content-Encoding'] = 'deflate'
        return zlib.compress(data), headers

    async def on_request_start(self,
                               session, trace_config_ctx, params):
        print("Starting request")

    async def on_request_end(self, session, trace_config_ctx, params):
        print("Ending request")

    def set_trace_config(self):
        """
        async with aiohttp.ClientSession(
                trace_configs=[trace_config]) as client:
            client.get('http://example.com/some/redirect/')
        async with aiohttp.ClientSession(
                trace_configs=[AuditRequest(), XRay()]) as client:
            client.get('http://example.com/some/redirect/')
        :return:
        """
        # from mylib.traceconfig import AuditRequest
        # from mylib.traceconfig import XRay
        trace_config = aiohttp.TraceConfig()
        trace_config.on_request_start.append(self.on_request_start)
        trace_config.on_request_end.append(self.on_request_end)

    def tpc_conn(self, limit=100, limit_per_host=30,
                 ttl_dns_cache=300, use_dns_cache=False, resolver=None):
        """
        默认情况下，会话对象获得连接器的所有权，此外，一旦关闭会话，连接对象也会关闭连接。
        如果您希望通过不同的会话 实例共享同一连接器，
        则必须 为每个会话实例将 connector_owner参数设置为False。


        :param limit:   要限制同时打开的连接数，您可以将limit 参数传递给连接器：
        如果您明确希望没有限制，请传递0。例如：conn = aiohttp.TCPConnector(limit=0)
        :param limit_per_host:    要限制到同一端点（三重）的同时打开的连接数，可以将limit_per_host 参数传递给connector：(host, port, is_ssl)
        该示例将并行连接的数量限制为30个。
        默认值为0（每个主机没有限制）。
        :param ttl_dns_cache:   要限制到同一端点（三重）的同时打开的连接数，可以将limit_per_host 参数传递给connector：(host, port, is_ssl)
        该示例将并行连接的数量限制为30个。
        默认值为0（每个主机没有限制）。
        :param use_dns_cache:或禁用DNS缓存表的使用，这意味着所有请求最终都会做出DNS解析，如以下示例所示：
        :param resolver:  resolver = AsyncResolver(nameservers=["8.8.8.8", "8.8.4.4"])
        :return:
        """
        connector = aiohttp.TCPConnector(limit=limit, limit_per_host=limit_per_host,
                                         ttl_dns_cache=ttl_dns_cache, use_dns_cache=use_dns_cache,
                                         resolver=resolver)
        return connector

    def unix_conn(self,path):
        conn = aiohttp.UnixConnector(path=path)
        return conn

    def windows_conn(self,path):
        """
        它仅适用于ProactorEventLoop
        :param path:
        :return:
        """
        conn = aiohttp.NamedPipeConnector(path=path)
        return conn

    def get_cookie_jar(self):
        """
        session.get(
        'http://httpbin.org/cookies/set?my_cookie=my_value')
        filtered = session.cookie_jar.filter_cookies(
        'http://httpbin.org')
        assert filtered['my_cookie'].value == 'my_value'
        :return:
        """
        return self.session.cookie_jar

    def url(self, url, encoded=True):
        """
        传递参数将覆盖encoded=True，切勿同时使用这两个选项。
        self.params 为 传递参数
        aiohttp在发送请求之前在内部执行URL 规范化。
        册封编码主机通过部分IDNA编解码器和适用 requoting到路径和查询部分。
        例如URL('http://example.com/путь/%30?a=%31')转换为 URL('http://example.com/%D0%BF%D1%83%D1%82%D1%8C/0?a=1')。
        如果服务器接受精确的表示并且不重新引用URL本身，则有时不希望进行规范化。
        :param url:
        :param encoded: 要禁用规范化，请使用encoded=True参数进行URL构建
        :return:
        """
        return URL(url, encoded=encoded)

    def get(self):
        """
        如果您需要设置自定义ssl参数（例如，使用自己的认证文件），则可以创建一个ssl.SSLContext实例并将其传递给适当的ClientSession方法
        sslcontext = ssl.create_default_context(
            cafile='/path/to/ca-bundle.crt')
        如果需要验证自签名证书，则可以执行与上一个示例相同的操作，但是ssl.SSLContext.load_cert_chain()使用密钥对添加另一个调用 ：
        sslcontext = ssl.create_default_context(
        cafile='/path/to/ca-bundle.crt')
        sslcontext.load_cert_chain('/path/to/client/public/device.pem',
                                   '/path/to/client/private/device.key')
        ssl验证失败时存在显式错误
        aiohttp.ClientConnectorSSLError
        ssl=False aiohttp对HTTPS协议使用严格检查。认证检查可以通过设置适当放宽
        :return:
        """
        pass

    def post(self):
        pass

    def put(self):
        pass

    def delete(self):
        pass

    def head(self):
        pass

    def options(self):
        pass

    def patch(self):
        pass

    def rsp(self):
        """
        print(resp.status)
        print(await resp.text())
        aiohttp自动解码服务器中的内容。您可以为该text()方法指定自定义编码：
        await resp.text(encoding='windows-1251')
        对于非文本请求，您还可以字节形式访问响应主体：
        print(await resp.read())
        br编码解码需要：
        https://github.com/python-hyper/brotlipy
        # 如果JSON解码失败，json()将引发异常。可以为json()调用指定自定义编码和解码器功能。
        print(await resp.json())
        # 上面的方法将整个响应主体读入内存。如果您打算读取大量数据，请考虑使用下面记录的流响应方法。
        # 您可以使用该content 属性。它是aiohttp.StreamReader 该类的一个实例。
        # 在gzip和deflate转移编码自动进行解码为您提供：
        with open(filename, 'wb') as fd:
            while True:
                chunk = await resp.content.read(chunk_size)
                if not chunk:
                    break
                fd.write(chunk)

        print(await resp.headers)
        # 但如果服务器使用非标准编码，则有时需要未转换的数据。
        这些标头的格式不正确RFC 7230的 角度来看，可以通过使用
        print(await resp.raw_headers)
        如果响应包含一些HTTP Cookie，则可以快速访问它们：
        响应Cookie仅包含重定向链中最后一个请求的Set-Cookie标头中的值。
        要在所有重定向请求之间收集cookie，请使用aiohttp.ClientSession对象。
        print(await resp.cookies)
        # 如果请求被重定向，则可以使用history属性查看先前的响应：
        如果未发生重定向或将其allow_redirects设置为False，则历史记录将为空序列。
        print(await resp.history)
        显式地传递期望的类型（在这种情况下，检查将是严格的，没有扩展格式的支持，因此custom/xxx+type将不被接受）：
        await resp.json(content_type='custom/type')。
        完全禁用检查：
        await resp.json(content_type=None)。
        :return:
        """
        pass

    def multipart(self):
        """
        https://docs.aiohttp.org/en/stable/multipart.html#aiohttp-multipart
        :return:
        """
        pass

    def close(self):
        self.session.close()

    def __del__(self):
        self.close()
