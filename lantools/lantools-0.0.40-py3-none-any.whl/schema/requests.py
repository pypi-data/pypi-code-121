from pydantic import BaseModel
import requests
from requests.adapters import HTTPAdapter
from .. import decorator

class HttpRequest(BaseModel):
    retry_times: int = 5 # http 重试次数
    timeout:int = 30    # 超时时间

    @decorator.singleton
    def requests(self) -> requests.Session:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=self.retry_times))
        s.mount('https://', HTTPAdapter(max_retries=self.retry_times))
        return s

    def post(self, url, data):
        return self.requests().post(url, json=data, timeout=self.timeout)
            