import time
from urllib import parse, request


def notify(token,msg):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 5.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/48.0.2564.82 Safari/537.36'}
    localtime = time.asctime( time.localtime(time.time()) )
    # print(localtime+'\n'+responses)
    data = parse.urlencode({'text': localtime+'\n'+msg}).encode()
    req = request.Request(
        "https://api.chanify.net/v1/sender/"+token.strip()+'?sound=1',
        data=data)
    request.urlopen(req)
    print("已通知，"+"本地时间为 :"+ localtime)