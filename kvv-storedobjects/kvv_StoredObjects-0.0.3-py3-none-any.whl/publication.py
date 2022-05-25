import datetime
from prettytable import PrettyTable


class Publication:
    defaultDate = datetime.datetime(1970, 1, 1)

    def __init__(self):
        self.title = ""
        self.authors = []
        self.type = ""
        self.issn = None
        self.doi = None
        self.eid = None
        self.scopusId = None
        self.pii = None
        self.ut = None  # wos
        self.publishedDate = Publication.defaultDate
        self.indexedDate = Publication.defaultDate
        self.citations = 0
        self.publisher = ""
        self.containerTitle = []
        # self.pages = "" # для статьи в журнале

    def MergeIDs(self, anotherPubl):
        if anotherPubl is None:
            return

        if self.eid is None:
            self.eid = anotherPubl.eid
        if self.scopusId is None:
            self.scopusId = anotherPubl.scopusId
        if self.pii is None:
            self.pii = anotherPubl.pii
        if self.ut is None:
            self.ut = anotherPubl.ut

    def __str__(self):
        table = PrettyTable()
        table.header = False
        table._max_width = {"Field 1": 20, "Field 2": 70}

        table.add_row(["Название", self.title[0]])
        table.add_row(["ISSN", self.issn])
        table.add_row(["DOI", self.doi])
        table.add_row(["EID", self.eid])
        table.add_row(["Scopus ID", self.scopusId])
        table.add_row(["PII", self.pii])
        table.add_row(["Дата публикации", str(self.publishedDate)])
        table.add_row(["Дата индексирования", str(self.indexedDate)])
        table.add_row(["Число цитирований", self.citations])
        table.add_row(["Издатель", self.publisher])
        table.add_row(["Источник", self.containerTitle])
        return table.get_string()


