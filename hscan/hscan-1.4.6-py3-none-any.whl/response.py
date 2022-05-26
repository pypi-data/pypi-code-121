import json
import chardet
from bs4 import BeautifulSoup
from scan.common import logger


class Response:
    def __init__(self):
        self.__req_resp = None
        self.status_code = None
        self.message = ''
        self.ok = False
        self.client = None
        self.request_url = None

    async def aclose(self):
        if self.__req_resp:
            try:
                await self.__req_resp.aclose()
            except:
                pass
        if self.client:
            try:
                await self.client.aclose()
            except:
                pass

    @property
    def response(self):
        return self.__req_resp

    @response.setter
    def response(self, req_resp):
        self.__req_resp = req_resp
        self.status_code = req_resp.status_code

    def json(self):
        try:
            return json.loads(self.__req_resp.content)
        except Exception as e:
            logger.error(f'格式化json异常:{e}, 链接:{self.request_url}')

    def soup(self):
        try:
            soup = BeautifulSoup(self.__req_resp.content, 'lxml')
            return soup
        except Exception as e:
            logger.error(f'格式化soup异常:{e}, 链接:{self.request_url}')

    def text(self):
        try:
            return self.__req_resp.content.decode()
        except UnicodeDecodeError:
            try:
                encoding = chardet.detect(self.__req_resp.content).get('encoding')
                return self.__req_resp.content.decode(encoding)
            except Exception as e:
                logger.error(f'格式化text异常:{e}')
        except Exception as e:
            logger.error(f'格式化text异常:{e}, 链接:{self.request_url}')

    def content(self):
        try:
            content = self.__req_resp.content
            return content
        except Exception as e:
            logger.error(f'获取content异常:{e}, 链接:{self.request_url}')



