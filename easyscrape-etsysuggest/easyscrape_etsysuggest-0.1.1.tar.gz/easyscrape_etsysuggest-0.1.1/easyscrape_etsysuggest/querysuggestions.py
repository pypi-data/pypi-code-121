import requests
import urllib.parse
import json

def query(term):
    term=urllib.parse.quote(term.lower())
    # set headers
    header = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36','Referer':'https://www.etsy.com/'}

    # define url
    url = f"https://www.etsy.com/suggestions_ajax.php?version=10_12672349415_19&search_query={term}&search_type=all"

    # store http request into html variable
    html = requests.get(url,params=None,headers=header)
    results = html.json()

    resultlist = []
    
    for result in results["results"]:
        resultlist.append(result["query"])

    # Remove last element
    resultlist = resultlist[:-1]
    return resultlist

print(query("Monty Python"))