import requests
import json
from crossref.restful import Works
from StoredObjects import Publication
from StoredObjects import University
from datetime import datetime

baseUrl = 'https://api.crossref.org/'

def getPublicationByDOI(doi):
    works = Works()
    work = works.doi(doi)
    if work is None:
        return None
    publ = Publication()
    publ.title = work['title']
    publ.type = work['type']
    publ.doi = work['DOI']
    if 'ISSN' in work:
        publ.issn = work['ISSN']
    publ.citations = work['is-referenced-by-count']
    publ.publisher = work['publisher']
    publ.publishedDate = work['published']['date-parts']
    publ.indexedDate = work['indexed']['date-parts']

    publ.containerTitle = work['container-title']

    authors = work['author']
    for authorDict in authors:
        if 'given' in authorDict:
            savedAuthor = University.getUniversity().getCrossrefAuthor(authorDict['given'], authorDict['family'])
            publ.authors.append(savedAuthor)

    return publ


def getPublicationsByPeriod(author, fromDate, toDate):
    splitName = author.engName.split(' ')
    family = splitName[0]
    given = splitName[1]
    queryName = given + ' ' + family
    dateFormat = '%Y-%m-%d'
    fromFormat = 'from-created-date:' + fromDate.strftime(dateFormat)
    toFormat = 'until-created-date:' + toDate.strftime(dateFormat)

    query = baseUrl + 'works?query.author=' + queryName + '&filter=' + fromFormat + ',' + toFormat

    
    response = requests.get(query)
    json_str = response.text
    x = json.loads(json_str)

    publications = []

    items = x['message']['items']
    for item in items:
        correctAuthor = False
        authors = item['author']
        for au in authors:
            if 'given' not in au.keys():  # в авторах может быть универ
                continue

            if au['given'].startswith(given) and au['family'] == family \
                    or au['family'].startswith(given) and au['given'] == family:  # имя и фамилия могут быть изменены местами
                secondName = ''
                if len(splitName) > 2:
                    secondName = splitName[2][0] + '.'

                if au['given'] == given or au['given'] == given + ' ' + secondName:
                    correctAuthor = True

        if correctAuthor:
            doi = item['DOI']
            publ = getPublicationByDOI(doi)
            if publ is None:
                continue
            # publ.Merge(scopus_api.IndexRetrieval(doi))

            publications.append(publ)

            # createdTimeStamp = item['created']['timestamp']
            # createdDate = datetime.fromtimestamp(createdTimeStamp / 1000)
            #
            # print(item['title'][0], au['given'], au['family'])
            # text += item['title'][0] + '\n'
            # text += au['given'] + ' ' + au['family'] + ', ' + createdDate.strftime(dateFormat)
            # text += '\n---------------------\n'

    return publications
