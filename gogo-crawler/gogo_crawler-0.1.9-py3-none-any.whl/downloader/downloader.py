import logging
import pathlib
from enum import Enum
import random

from pySmartDL import SmartDL
import urllib


class Statuses(Enum):
    IDLE = 1
    DOWNLOADING = 2
    FAILED = 3
    SUCCESS = 4


class Downloader:
    class Request:
        def __init__(self, url, proxy=[], enable_proxy=True) -> None:
            self.url = url
            self.proxies = proxy
            self.enable_proxy = enable_proxy

        def get_proxy(self):
            if not self.proxies:
                return None
            ret = {}
            proxy = random.choice(self.proxies)
            ret['http'] = proxy
            ret['https'] = proxy
            return ret

    def __init__(self, referer='goload.pro'):
        self.referer = referer

    def status(self):
        return self.status

    def download(self, series_name, episode, location, request: Request):
        url = request.url
        try:

            folder_name = series_name.lower().strip().replace(' ', '_').replace('-', '_')
            folder_name = ''.join(ch for ch in folder_name if ch not in set('.:;%^&*@#$!'))
            file_name = location + '/' + folder_name + '/' + folder_name + '_episode_' + str(episode) + '.mp4'
            path = pathlib.Path(location + '/' + folder_name)
            path.mkdir(parents=True, exist_ok=True)
            headers = {}
            if 'user-agent' not in headers:
                headers['user-agent'] = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Gecko/20100101Firefox/56.0"

            # This allows backwards compatible while also working with
            # PySmartDl as it only passes user agent if spelled "User-Agent"
            headers['User-Agent'] = headers.pop('user-agent')

            if self.referer:
                headers['Referer'] = self.referer

            request_args = {'headers': headers}
            if request.enable_proxy and request.get_proxy():
                proxy_support = urllib.request.ProxyHandler(request.get_proxy())
                opener = urllib.request.build_opener(proxy_support)
                urllib.request.install_opener(opener)
            dest = str(file_name)  # str(path.parent.absolute())
            obj = SmartDL(url, dest, request_args=request_args, progress_bar=True, verify=True)
            obj.start()
            if not obj.isSuccessful():
                raise Exception("SmartDL had issues downloading file")
            elif obj.get_final_filesize() == 0:
                raise Exception("Downloaded filesize is 0")
            return file_name
        except Exception as err:
            logging.error("Error downloading series {0} episode {1} at url {2} to file location {3} with error {4}"
                          , series_name, episode, url, location, err)
            raise Exception("Error downloading series {0} episode {1} at url {2} to file location {3} with error {4}"
                            .format(series_name, episode, url, location, err)) from err
# d = Downloader()
# d.download("Kimetsu no Yaiba: Yuukaku-hen",11,".","https://gogo-cdn.com/download.php?url=aHR0cHM6LyAawehyfcghysfdsDGDYdgdsfsdfwstdgdsgtert9URASDGHUSRFSJGYfdsffsderFStewthsfSFtrftesdfjZG4zNy5hbmljZG4uc3RyZWFtL3VzZXIxMzQyL2Y0NDU1YjU3ZTgzYjMxYWU5N2JjZTNjMGFjY2ZiMWEzL0VQLjExLnYwLjE2NDQ3Njk1MDIuMTA4MHAubXA0P3Rva2VuPTJNZDFicy1HcWhqSHhrbmxlQWw1ZVEmZXhwaXJlcz0xNjQ5NTQxMjczJmlkPTE4MDQ5Ng==")
