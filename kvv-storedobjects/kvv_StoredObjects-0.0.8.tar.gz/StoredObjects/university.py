import requests
from bs4 import BeautifulSoup
import pickle
from .department import Department

class University:
    _saveFile = "univer_save.pickle"
    _univer = None


    def __init__(self):
        self.departments = []
        self.loadData()
        if not self.departments:
            self.fillDepartments()
        self.saveData()

    @staticmethod
    def getUniversity():
        if University._univer is None:
            University._univer = University()
        return University._univer

    def fillDepartments(self):
        cafsLink = 'https://www.mstu.edu.ru/structure/kafs/'
        html = requests.get(cafsLink).text
        soup = BeautifulSoup(html, features="html.parser")
        lists = soup.findAll("ul", {"class": "anker"})
        # print(lists)
        links = []
        for ul in lists:
            hrefs = ul.findAll("a")
            for h in hrefs:
                links.append(h['href'])
        print(links)
        baseUrl = 'https://www.mstu.edu.ru'
        for link in links:
            url = baseUrl + link
            self.addDepartment(url)

    def addDepartment(self, link):
        dep = Department(link)
        self.departments.append(dep)

    def getDepartment(self, name):
        for dep in self.departments:
            if name == dep.name:
                return dep
        return None

    def getDepartmentNames(self):
        names = []
        for dep in self.departments:
            names.append(dep.name)
        return names

    def searchEmployees(self, name):
        names = []
        for dep in self.departments:
            names.extend(dep.searchEmployees(name))
        return names

    def getAuthor(self, fullName):
        empls = []
        for dep in self.departments:
            empl = dep.findEmployee(fullName)
            if empl is not None:
                empls.append(empl)
        if len(empls) != 1:
            return None
        return empls[0]

    def loadData(self):
        try:
            with open(University._saveFile, 'rb') as f:
                copy = pickle.load(f)
                if copy is not None:
                    self.departments = copy.departments
        except EnvironmentError:
            pass

    def saveData(self):
        with open(University._saveFile, 'wb') as f:
            pickle.dump(self, f)
