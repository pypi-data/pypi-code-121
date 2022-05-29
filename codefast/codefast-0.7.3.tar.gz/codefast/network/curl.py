
import subprocess
from typing import Dict, List, Any
import json


class Curl(object):
    """Curl wrapper"""

    def __init__(self, url: str = '', silence: bool = True) -> None:
        self.cmd = ['curl', '-X', 'POST', url]
        if silence:
            self.cmd.append('-s')

    def set_url(self, url: str):
        self.cmd[3] = url
        return self

    def set_method(self, method: str = 'POST'):
        self.cmd[2] = method
        return self

    def set_timeout(self, timeout: int):
        self.cmd.extend(['-m', str(timeout)])
        return self

    def set_retry(self, retry: int):
        self.cmd.extend(['--retry', str(retry)])
        return self

    def set_headers(self, headers: Dict[str, str]):  # -> Curl
        for k, v in headers.items():
            self.cmd.extend(['-H', '{}: {}'.format(k, v)])
        return self

    def add_form_data(self, form_data: Dict[str, str]):
        for k, v in form_data.items():
            self.cmd.extend(['-F', '{}={}'.format(k, v)])
        return self

    def run(self):
        self.res = subprocess.check_output(self.cmd).decode('utf-8')
        return self

    def json(self) -> Dict[str, Any]:
        return json.loads(self.res)
