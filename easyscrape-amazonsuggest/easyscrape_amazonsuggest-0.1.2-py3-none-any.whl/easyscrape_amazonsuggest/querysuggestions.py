import requests,json
from random import randint

def query(term):

    seq = randint(1000000,9999999)

    # set headers
    header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36','Referer':'https://www.google.com/'}

    # define url
    url = f"https://completion.amazon.com/api/2017/suggestions?limit=11&prefix={term}&suggestion-type=WIDGET&suggestion-type=KEYWORD&page-type=Gateway&alias=aps&site-variant=desktop&version=3&event=onKeyPress&wc=&lop=en_US&fb=1&session-id=131-{seq}-4362167&request-id=REKRP72XTYGR80EQ3GPZ&mid=ATVPDKIKX0DER&plain-mid=1&client-info=amazon-search-ui"

    # store http request into html variable
    html = requests.get(url,params=None,headers=header)
    results = html.json()

    resultlist = []
    
    for result in results["suggestions"]:
        resultlist.append(result["value"])

    return resultlist