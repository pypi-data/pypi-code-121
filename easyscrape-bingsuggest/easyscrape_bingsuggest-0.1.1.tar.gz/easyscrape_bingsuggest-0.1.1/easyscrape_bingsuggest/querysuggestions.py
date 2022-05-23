import requests
from bs4 import BeautifulSoup
from random import randint

def query(term):

    seq = randint(1000000,9999999)

    # set headers
    header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36','Referer':'https://www.google.com/'}

    # define url
    url = f"https://www.bing.com/AS/Suggestions?pt=page.serp&mkt=en-us&qry={term}&asv=1&cp=14&msbqf=false&cvid=B69DCD8{seq}45DDA0286DBD1867F"

    # store http request into html variable
    html = requests.get(url,params=None,headers=header)

    htmlcontent = (html.content).decode()
    BS_Parser = BeautifulSoup(htmlcontent,'html.parser')

    items = BS_Parser.select('strong')

    resultlist = []
    
    for result in items:
        resultlist.append(result.text.strip())
    
    #print(BS_Parser)
    return resultlist

print(query("Monty Python"))