from transliterate import translit
from bs4 import BeautifulSoup


class Author:

    def __init__(self, name):
        self.name = name
        self.engName = translit(name, 'ru', reversed=True)
        self.crossrefName = []
        self.scopusName = []
        self.affiliations = []
        self.orcid = None
        self.publications = []

    def getScopusName(self):
        if not self.scopusName:
            splitName = self.engName.split(' ')
            self.scopusName = (splitName[0], splitName[1][0] + '.' + splitName[2][0] + '.')
        return self.scopusName

