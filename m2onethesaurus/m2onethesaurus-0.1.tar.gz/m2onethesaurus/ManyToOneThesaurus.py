from bs4 import BeautifulSoup
import urllib3
import lxml

class ManyToOneThesaurus:

    def get_word_input(self) -> list:
        words = input("Please enter words separated by commas.\n").replace(" ", "").split(",")
        return words

    def __init__(self) -> None:
        self._dict = {}

    def _get_site_by_word(self, word) -> any:
        site = "https://www.wordhippo.com/what-is/another-word-for/" + word.lower().replace("-", "_").replace(" ","_") + ".html"
        http = urllib3.PoolManager()
        source = http.request('GET', site)
        return source

    def query(self, words, depth) -> dict:
        self._dict = {}
        self._num_words = len(words)
        for word in words:
            banned = []
            site = self._get_site_by_word(word)
            if site.status == 200:
                soup = BeautifulSoup(site.data, "lxml")
                related_words = soup.find_all("div", class_="relatedwords")
                for i, s in enumerate(related_words):
                    p=s.find_all("div", class_="wb", limit=depth)
                    for k, w in enumerate(p):
                        wl = w.find("a").text
                        if wl not in banned and wl not in words:
                            strength = ((len(p)-k)/len(p))
                            if wl in self._dict:
                                self._dict[wl] += [strength]
                            else:
                                self._dict[wl] = [strength]
                            banned.append(wl)
        for k, v in self._dict.items():
            v += [0] * (len(words)-len(v))
        marklist = sorted(self._dict.items(), key=lambda x:((sum(x[1])/len(x[1]))/(1+max(x[1])-min(x[1]))))[::-1]
        self._dict = dict(marklist)
        return self._dict
        
    def print_results(self, limit):
        count = 0
        for word, heat in self._dict.items():
            if count < limit:
                h_count = sum(h > 0 for h in heat)
                metric = (sum(heat)/len(heat))
                metric/=(1+max(heat)-min(heat))
                print(word + ": confidence of " + str(metric) + ", appears in " + str(h_count) + " out of " + str(len(heat)) + " entry(s)" )
                count+=1

    def find_word(self, word) -> tuple:
        if word in self._dict:
            return (word, self._dict[word])

    def clear(self):
        self._dict = {}
