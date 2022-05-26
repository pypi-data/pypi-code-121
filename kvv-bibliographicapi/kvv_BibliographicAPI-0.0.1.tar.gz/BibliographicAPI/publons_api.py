import requests
import json
from StoredObjects import Author, Publication

token = None
baseUrl = 'https://publons.com/api/v2/'


def _request(url):
    if token == None:
        print("Publons token was not provided")
        return
    headers = {'Authorization': 'Token ' + token, 'Content-Type': 'application/json'}
    url = url.removeprefix(baseUrl)
    r = requests.get(baseUrl + url, headers=headers)
    if r.status_code != 200:
        raise Exception("Publons returned an error:\n" + r.text)
    try:
        r = r.json()
        if "detail" in r:
            if (r['detail'] == 'Invalid token.'):
                print("Publons token is invalid")
        else:
            return r
    except:
        print('There was an error communiating with the Publons API')


def getAuthorsOfUniversity():
    inst = 'Murmansk State Technical University'
    url = 'academic/?institution=' + inst
    json_obj = _request(url)
    while True:
        print(json_obj['count'])

        url = json_obj['next']
        if url is None:
            break
        json_obj = _request(url)
    
def getPublicationsOfAuthor(author: Author):
    publications = []
    url = 'academic/publication/?academic=' + author.orcid
    json_obj = _request(url)
    while True:
        results = json_obj['results']
        for res in results:
            info = res['publication']
            
            publ = Publication()
            publ.title = info['title']
            if info['ids'] is not None:
                ids = info['ids']
                publ.doi = ids['doi']
                publ.ut = ids['ut']
            publications.append(publ)

        
        url = json_obj['next']
        if url is None:
            break
        json_obj = _request(url)
    return publications