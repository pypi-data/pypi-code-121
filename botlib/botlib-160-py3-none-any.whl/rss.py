# This file is placed in the Public Domain.


"rich site syndicate"


import html.parser
import re
import threading
import urllib


from .hdl import Bus
from .obj import Object, get, update
from .obj import Class, Config, find, last, save, spl
from .tmr import Repeater
from .thr import launch


from urllib.error import HTTPError, URLError
from urllib.parse import quote_plus, urlencode
from urllib.request import Request, urlopen


def __dir__():
    return (
        "Feed",
        "Rss",
        "Seen",
        "Fetcher",
        "display",
    )


class Feed(Object):

    def __getattr__(self, key):
        try:
            return super().__getitem__(key)
        except KeyError:
            self[key] = ""
            return self[key]


class Rss(Object):

    def __init__(self):
        super().__init__()
        self.display_list = "title,link,author"
        self.name = ""
        self.rss = ""


class Seen(Object):

    def __init__(self):
        super().__init__()
        self.urls = []


class Fetcher(Object):

    dosave = False
    errors = []
    seen = Seen()

    def __init__(self):
        super().__init__()
        self.connected = threading.Event()

    def display(self, o):
        result = ""
        dl = []
        try:
            dl = o.display_list or "title,link"
        except AttributeError:
            dl = "title,link,author"
        for key in spl(dl):
            if not key:
                continue
            data = get(o, key, None)
            if not data:
                continue
            data = data.replace("\n", " ")
            data = striphtml(data.rstrip())
            data = unescape(data)
            result += data.rstrip()
            result += " - "
        return result[:-2].rstrip()

    def fetch(self, feed):
        counter = 0
        objs = []
        for o in reversed(list(getfeed(feed.rss, feed.display_list))):
            if not o:
                continue
            f = Feed()
            update(f, o)
            update(f, feed)
            if "link" in f:
                u = urllib.parse.urlparse(f.link)
                if u.path and not u.path == "/":
                    url = "%s://%s/%s" % (u.scheme, u.netloc, u.path)
                else:
                    url = f.link
                if url in Fetcher.seen.urls:
                    continue
                Fetcher.seen.urls.append(url)
            counter += 1
            if self.dosave:
                save(f)
            objs.append(f)
        if objs:
            save(Fetcher.seen)
        txt = ""
        name = get(feed, "name")
        if name:
            txt = "[%s] " % name
        for o in objs:
            txt2 = txt + self.display(o)
            Bus.announce(txt2.rstrip())
        return counter

    def run(self):
        thrs = []
        for _fn, o in find("rss"):
            thrs.append(launch(self.fetch, o))
        return thrs

    def start(self, repeat=True):
        last(Fetcher.seen)
        if repeat:
            repeater = Repeater(300.0, self.run)
            repeater.start()



class Parser(Object):

    @staticmethod
    def getitem(line, item):
        try:
            i = line.index("<%s>" % item) + len(item) + 2
            ii = line.index("</%s>" % item)
        except ValueError:
            return
        l = line[i:ii]
        if "CDATA" in l:
            l = l.replace("![CDATA[", "")
            l = l.replace("]]", "")
            l = l[1:-1]
        return l


    @staticmethod
    def parse(txt, items="title,link"):
        res = []
        for line in txt.split("<item>"):
            line = line.strip()
            o = Object()
            for item in spl(items):
                o[item] = Parser.getitem(line, item)
            res.append(o)
        return res



def getfeed(url, items):
    if Config.debug:
        return [Object(), Object()]
    try:
        result = geturl(url)
    except (ValueError, HTTPError, URLError):
        return [Object(), Object()]
    if not result:
        return [Object(), Object()]
    return Parser.parse(str(result.data, "utf-8"), items)


def gettinyurl(url):
    postarray = [
        ("submit", "submit"),
        ("url", url),
    ]
    postdata = urlencode(postarray, quote_via=quote_plus)
    req = Request("http://tinyurl.com/create.php",
                  data=bytes(postdata, "UTF-8"))
    req.add_header("User-agent", useragent(url))
    for txt in urlopen(req).readlines():
        line = txt.decode("UTF-8").strip()
        i = re.search('data-clipboard-text="(.*?)"', line, re.M)
        if i:
            return i.groups()
    return []


def geturl(url):
    url = urllib.parse.urlunparse(urllib.parse.urlparse(url))
    req = urllib.request.Request(url)
    req.add_header("User-agent", useragent("oirc"))
    response = urllib.request.urlopen(req)
    response.data = response.read()
    return response


def striphtml(text):
    clean = re.compile("<.*?>")
    return re.sub(clean, "", text)


def unescape(text):
    txt = re.sub(r"\s+", " ", text)
    return html.unescape(txt)


def useragent(txt):
    return "Mozilla/5.0 (X11; Linux x86_64) " + txt


parser = Parser()


Class.add(Feed)
Class.add(Rss)
Class.add(Seen)
