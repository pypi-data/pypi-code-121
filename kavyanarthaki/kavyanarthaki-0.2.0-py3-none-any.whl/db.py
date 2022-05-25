#!/usr/bin/python3
import pkg_resources
import csv, codecs, requests

class data:
    def __init__(self):
        self.data = []
        self.dictionary = {}
        
    def update(self):
        self.dictionary = {}
        for entry in self.data:
            self.dictionary[str(entry[-1]).upper()] = entry
    
    def load(self,filelocation=''):
        if filelocation == '':
            filelocation = 'data/data.csv'
            buffered_reader = pkg_resources.resource_stream(__name__,filelocation)
            csvfile = csv.reader(codecs.iterdecode(buffered_reader,'UTF-8'))
            self.data = []
            for row in csvfile:
                self.data.append(row)
        else:
            with open(filelocation, 'r', encoding='UTF-8') as csvfile:
                csvreader = csv.reader(csvfile)
                self.data = []
                for row in csvfile:
                    self.data.append(row.rstrip().split(sep=','))
        self.update()
            
    def loadurl(self,url):
        webresponse = requests.get(url)
        csvfile = codecs.iterdecode(webresponse.iter_lines(), 'UTF-8')
        csvreader = csv.reader(csvfile)
        self.data = []
        for row in csvreader:
            self.data.append(row)
        self.update()
    
    def check(self,sequence):
        return self.dictionary.get(sequence.upper(),'No Entry Found')
