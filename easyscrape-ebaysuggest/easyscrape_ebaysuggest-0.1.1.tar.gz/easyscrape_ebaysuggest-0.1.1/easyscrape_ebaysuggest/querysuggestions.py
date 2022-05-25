import requests
import json

def query(term):


    # set headers
    header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36','Referer':'https://www.google.com/'}

    # define url
    url = f"https://www.ebay.com/autosug?kwd={term}&_jgr=1&sId=0&_ch=0&_store=1&_help=1&callback=0"

    # store http request into html variable
    html = requests.get(url,params=None,headers=header)
    results = html.json()

    resultlist = []
    
    for result in results["res"]["sug"]:
        resultlist.append(result)

    return resultlist