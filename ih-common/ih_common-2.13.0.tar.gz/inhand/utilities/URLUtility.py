from urllib.parse import urlparse

class GenericURL:
    def __init__(self,url):
        self.url = url
        parsed = urlparse(url)
        self.scheme = parsed.scheme
        self.host = parsed.netloc
        self.path = parsed.path
        self.params=GenericURL.parseParams(parsed.query)

    @staticmethod
    def parseParams(query):
        params = {}
        if query is not None and '' != query:
            list = query.split("&")
            for s in list:
                index = s.index("=")
                if index > -1:
                    params[s[0:index]] = s[index+1:]
        return params

if __name__ == '__main__':
    str="http://api.map.baidu.com:8801/geocoder/v2/d?ad=34&ak=wo5GfWYQ0VEhLn2ZRfl1v3l0auM2MnaR&b=1"
    url = GenericURL(str)
    print(url.path)