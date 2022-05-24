try:
    from bs4 import BeautifulSoup
except:
    pass

try:
    from serpapi.google_search_results import GoogleSearchResults
except:
    pass

#from googlesearch import search

from dataclasses import field
from itertools import cycle
import requests, re, os
import numpy as np

from . import io_lib, string_lib

try:    
    proxies     = io_lib.get_proxies()
except:
    proxies = ()
proxy_pool  = cycle(proxies)

class Search():
    prices:list  = field(default_factory = lambda: [])
    words:dict   = field(default_factory = lambda: {})

    def process(self,list_to_process):
        if type(list_to_process) == str:
            list_to_process = [list_to_process]

        i = 0
        for div in list_to_process:
            div_content = re.sub('<[^>]*>', '', str(div))

            prices = re.findall("(\d+.\d+,\d+ €|\d+,\d+ €|\d+.\d+ €)", div_content)
            if len(prices) != 0:
                for price in prices:
                    try:
                        rpl = price.replace('€','').replace(' ','').replace(',','.')
                        a = float(rpl)
                        self.prices.append(a)
                    except Exception as ex:
                        print(ex)
                    div_content = div_content.replace(price,'')

            words = string_lib.get_words(div_content)

            for word in words:
                word = word.lower()
                if not word in self.words:
                    self.words[word] = 1
                else:
                    self.words[word] += 1

    def join(self,search):
        for word in search.words:
            word = word.lower()
            if not word in self.words:
                self.words[word] = 1
            else:
                self.words[word] += 1
    
    def get_words(self):
        self.words =  string_lib.sort_words(self.words)
        return self.words

    def get_top_words(self):
        values  = list(set(list(self.words.values())))
        per     = np.percentile(values,60)
        words   = {x:y for x,y in self.words.items() if y > per}
        words   =  string_lib.sort_words(words)
        return words

    def print(self):
        words = self.get_top_words()
        
        for word, nb in words.items():
            print('%s %s'%(word,nb))

class Parser():

    def __init__(self,txt,element,classnames):
        txt = str(txt)
        regex_str = "<%s[^><]+class=[^><]+%s[^><]+>"%(element,classnames)
        found = re.findall(regex_str, str(txt))

        if len(found) != 0:
            divs        = re.findall("<%s"%element,str(txt))
            blocks_nb   = len(divs)
            parts       = txt.split('</%s>'%element)

        exit()

def remove_balise(txt):
    return re.sub('<[^>]*>', '', str(txt))

class GoogleEntry():
    title = ""
    host = ""
    link = ""
    desc = ""
    search = None

    def __init__(self,title,host,link,desc):
        self.title  = title
        self.host   = host.replace('http://','').replace('https://','').split('/')[0]
        self.link   = link
        self.desc   = desc
        self.search = Search()

    def analyze(self):
        self.search.process([self.title,self.desc])

    def set_global(self,search:Search):
        #print(self.search.words)
        pass

    def get_dict(self):
        return {'title':self.title,'host':self.host,'link':self.link,'desc':self.desc}

class GoogleSearch():
    words:dict = field(default_factory = lambda: {})

    def scrap_api(self,search_string):
        apikey = 'f22df9d6edeba41d3888a7384a4d945ed099efc202535f81ca4a58f6c7557afd'

        params = {
            "q" : search_string,
            "location" : "Grenoble, France",
            "hl" : "fr",
            "gl" : "fr",
            "google_domain" : "google.fr",
            "api_key" : apikey,
            "num":100
        }

        query               = GoogleSearchResults(params)
        dictionary_results  = query.get_dictionary()

        for key, config in dictionary_results.items():
            print(key,'\n', config)
        
        # save file
        file_name = '/tmp/trash/search.pkl'
        io_lib.archive_object(dictionary_results,file_name)
            
        if 'product_result' in dictionary_results:
            self.product = dictionary_results['produt_result']

        if 'organic_results' in dictionary_results:
            for element in dictionary_results['organic_results']:
                self.process_sequence(element['title'])
                self.process_sequence(element['snippet'])

                if 'rich_snippet' in element:
                    if 'top' in element['rich_snippet']:
                        if 'extensions' in element['rich_snippet']['top']:
                            self.process_list(element['rich_snippet']['top']['extensions'])

    def search(self,search_string,force=False):
        URL     = "https://www.google.com/search?"
        PARAMS  = {'q':search_string, 'num':100}
        proxy   = next(proxy_pool)
        #headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:20.0) Gecko/20100101 Firefox/20.0'}

        tmp_file = '/tmp/trash/%s.html'%search_string
        if not os.path.exists(tmp_file) or force:
            r       = requests.get(url = URL, params = PARAMS,timeout=2) #,proxies={"http": proxy, "https": proxy} 
            html    = r.text

            with open(tmp_file,'w') as f:
                f.write(html)
        else:
            with open(tmp_file,'r') as f:
                html = f.read()
        return html

    def scrap(self,search_string,force=False):
        if search_string == '': return

        print('Scrapping ...',search_string)

        html    = self.search(search_string,force)

        soup    = BeautifulSoup(html,"html.parser")

        # masters 
        entries         = []
        globals_text    = []
        mydivs          = soup.findAll("div", {"class": "ZINbbc xpd O9g5cc uUPGi"})
        for mydiv in mydivs:
            #parser  = Parser(div,"div", {"class": "ZINbbc xpd O9g5cc uUPGi"})
            #parser      = Parser(div,"div","ZINbbc xpd O9g5cc uUPGi")
            soup            = BeautifulSoup(str(mydiv),"html.parser")

            title, host, site, desc, link           = "", "", "", "", ""
            titledivs       = soup.findAll("div", {"class": "BNeawe vvjwJb AP7Wnd"})
            title_nb        = len(titledivs)

            if title_nb == 0:
                titledivs = soup.findAll("div", {"class": "MUxGbd v0nnCb aLF0Z"}) 
                title_nb        = len(titledivs)

            if title_nb != 0:
                title   = remove_balise(str(titledivs[0]))


            mydivs      = soup.findAll("div", {"class": "BNeawe UPmit AP7Wnd"})
            if len(mydivs) != 0:
                site        = remove_balise(mydivs[0])
                host        = site.split('›')[0].replace(' ','')

            mydivs      = soup.findAll("div", {"class": "BNeawe s3v9rd AP7Wnd"})
            if len(mydivs) != 0:
                desc        = remove_balise(mydivs[0])
            
            mydivs      = soup.findAll("a")
            if len(mydivs) != 0:
                link        = remove_balise(mydivs[0])

            globals_text.append(title)
            globals_text.append(desc)

            gentry = GoogleEntry(title,host,link,desc)
            gentry.analyze()

            #print(gentry.search.words)

            entries.append(gentry)

        # titles
        main = Search()
        main.process(globals_text)

        #for entry in entries:
        #    entry.set_global(main)

        #main.print()

        print(len(mydivs))
        print(mydivs[0])
        #print(sequences)
        #print(sites)

        #magasins  = soup.findAll("span")

        ret = []
        for entry in entries:
            ret.append(entry.get_dict())

        return ret
        
    def get_elements(self,elements_list):
        sequences = []
        for mydiv in elements_list:
            mydiv = re.sub('<[^>]*>', '', str(mydiv))
            sequences.append(mydiv)
        return sequences

