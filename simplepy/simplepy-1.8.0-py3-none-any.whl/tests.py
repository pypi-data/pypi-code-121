import requests

from simplepy import logger


class VerifyTest:
    @staticmethod
    def proxy_test(ip, gfw=False):
        """
        78.38.100.121:8080
        :param ip:
        :return:
        """
        proxies = {
            "http": f"http://{ip}",
            "https": f"http://{ip}"
        }
        if gfw:
            target_url = 'https://www.google.com/'
        else:
            target_url = "https://httpbin.org/ip"
        rep = requests.get(url=target_url, proxies=proxies, timeout=5)
        logger.info(rep.status_code)
        logger.info(rep.text)
