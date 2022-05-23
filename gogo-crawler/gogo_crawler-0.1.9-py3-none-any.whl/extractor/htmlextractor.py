'''
Extract downlaod url from Iframe of the page
https://gogo-cdn.com/download.php?url=aHR0cHM6LyURASDGHUSRFSJGYfdsffsderFStewthsfSFtrfteAdrefsdsdfwerFrefdsfrersfdsrfer36343534sdf9jZG4zMS5hbmljZG4uc3RyZWFtL3VzZXIxMzQyLzBlMGE5ZjVjMWJjNTgzOWViYjE2ZGE5MjU4NTFlMzI3L0VQLjEudjAuMTY0OTE3NzI4Mi4zNjBwLm1wND90b2tlbj1TT0p4R3Q5dGhNWTNYX0hLSlFNOU1RJmV4cGlyZXM9MTY0OTIwNjA2MSZpZD0xODM4MTY=
<iframe src="//gogoplay5.com/streaming.php?id=MTgzODE2&amp;title=Tomodachi+Game&amp;typesub=SUB&amp;sub=&amp;cover=Y292ZXIvdG9tb2RhY2hpLWdhbWUucG5n" allowfullscreen="true" frameborder="0" marginwidth="0" marginheight="0" scrolling="no"></iframe>


html link address https://gogoplay5.com/videos/shingeki-no-kyojin-the-final-season-part-2-episode-12.html
'''
import logging
import random
import re

import requests
from bs4 import BeautifulSoup
from requests_html import AsyncHTMLSession, HTMLSession


class HtmlExtractor:
    def __init__(self, html_url):
        self.html_url = html_url

    def extract_iframe_src(self):
        page = None
        try :
            page = requests.get(self.html_url, timeout=30)
            soup = BeautifulSoup(page.content, "html.parser")
            iframe = soup.find("iframe")
            src = iframe.get("src")
            return src
        except Exception as e:
            logging.error("Error finding iframe at url {0} with error {1}".format(self.html_url, e))
            raise Exception("Error finding iframe at url {0} with error {1}".format(self.html_url, e)) from e
        finally:
            if page:
                page.close()

class DynamicHtmlExtractor:
    class Request:
        def __init__(self, url, timeout=30, wait=2, sleep=3, proxies=[], enable_proxy=True, auth=None) -> None:
            self.url = url
            self.timeout = timeout
            self.wait = wait
            self.sleep = sleep
            self.proxies = proxies
            self.enable_proxy = enable_proxy
            self.auth = auth

        def get_proxy(self):
            if not self.proxies:
                return None
            ret = {}
            proxy = random.choice(self.proxies)
            ret['http'] = proxy
            ret['https'] = proxy
            return ret

    def __init__(self, html_url):
        self.html_url = html_url

    async def extract_download_div_class_parallel(self):
        result = []
        try:
            async_session = AsyncHTMLSession()
            r = await async_session.get(self.html_url)
            await r.html.arender()
            download_divs = r.html.find(".dowload")
            for div in download_divs:
                download_link_component = div.find("a")[0]
                download_link_text = download_link_component.text
                download_link = download_link_component.attrs['href']
                if 'gogo-cdn' in download_link:
                    video_meta = re.search(r'\((.*?)\)', download_link_text).group(0)
                    resolution = re.search(r'[0-9]+P', video_meta).group(0)
                    result.append((resolution, download_link))
        except Exception as e:
            logging.error("Error finding divs at url {0} with error {1}".format(self.html_url, e))
            raise Exception("Error finding divs at url {0} with error {1}".format(self.html_url, e)) from e
        finally:
            if async_session:
                async_session.close()
        result.reverse()
        return result

    def extract_download_div_class(self, request: Request) -> list:
        result = []
        proxy = request.get_proxy()
        header = {
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/74.0.3729.169 Safari/537.36",
            'referer': 'goload.pro'
        }
        page = None
        try:
            if not proxy or not request.enable_proxy:
                page = HTMLSession().get(self.html_url, headers=header, timeout=request.timeout)
            else:
                page = HTMLSession().get(self.html_url, headers=header, timeout=request.timeout, proxies=proxy)

            page.html.render(wait=request.wait, sleep=request.sleep)
            element = page.html.find('#content-download')[0]
            if element:
                captcha = element.html.find('iframe')
                if captcha > 0:
                    logging.error("Caught by captcha")
                    raise Exception("Caught by captcha")
            download_divs = page.html.find(".dowload")
            for div in download_divs:
                download_link_component = div.find("a")[0]
                download_link_text = download_link_component.text
                download_link = download_link_component.attrs['href']
                if 'gogo-cdn' in download_link:
                    video_meta = re.search(r'\((.*?)\)', download_link_text).group(0)
                    resolution = re.search(r'[0-9]+P', video_meta).group(0)
                    result.append((resolution, download_link))
        except Exception as e:
            logging.error("Error finding divs at url {0} with error {1}".format(self.html_url, e))
            raise Exception(
                "Error finding divs at url {0} with proxy {1} with error {2}".format(self.html_url, proxy, e)) from e
        finally:
            if page:
                page.close()
        result.reverse()
        return result

# resultloop = asyncio.new_event_loop()
# asyncio.set_event_loop(loop)
# d = DynamicHtmlExtractor('https://goload.pro/download?id=MTQxNDI1&title=Otome+Game+no+Hametsu+Flag+shika+Nai+Akuyaku+Reijou+ni+Tensei+shiteshimatta...&typesub=SUB&sub=&cover=Y292ZXIvb3RvbWUtZ2FtZS1uby1oYW1ldHN1LWZsYWctc2hpa2EtbmFpLWFrdXlha3UtcmVpam91LW5pLXRlbnNlaS1zaGl0ZXNoaW1hdHRhLnBuZw==&mip=0.0.0.0&refer=https://gogoplay5.com/&ch=d41d8cd98f00b204e9800998ecf8427e&op=1')
#
# res = loop.run_until_complete(d.extract_download_div_class_parallel())
# print(res)
