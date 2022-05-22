import spacy
from checklist.editor import Editor
import numpy as np
import collections
import re
# from checklist.building_blocks import fairness

def find_neg(text):
    negations = ['never', 'no', 'not', 'nobody', 'nothing', 'nowhere', 'neither', 'none']
    postfix = ['n\'t']
    prefix = ['non']
    ret = []
    for n in negations:
        ret.extend(re.findall(r'\b%s\b' % n, text.lower()))
    for n in postfix:
        ret.extend(re.findall(r'\b\w+%s\b' % n, text.lower()))
    for n in prefix:
        ret.extend([x for x in re.findall(r'\b%s\w*\b' % n, text.lower()) if x != 'none'])
    return ret

class Searcher:
    def __init__(self, dataset, subsample=10000, nlp=None):
        if nlp is None:
            self.nlp = spacy.load('en_core_web_sm')
        else:
            self.nlp = nlp
        self.editor = Editor()
        self.dataset = dataset
        if subsample and len(dataset) > subsample:
            ix = np.random.choice(len(dataset), subsample, replace=False)
            self.dataset = [dataset[i] for i in ix]
        self.parsed = list(self.nlp.pipe(self.dataset))

    def most_common(self, n=10, by_pos=False):
        counts = collections.Counter()
        counts_pos = collections.defaultdict(lambda: collections.Counter())
        for x in self.parsed:
            for y in x:
                counts[y.text]+= 1
                counts_pos[y.pos_][y.text] += 1
        if by_pos:
            ret = {}
            for p in counts_pos:
                ret[p] = [x[0] for x in counts_pos[p].most_common(n)]
            return ret
        return [x[0] for x in counts.most_common(n)]

    def search(self, string, n=3, ignore_case=True):
        if type(string) != str:
            string = '|'.join(string)
        else:
            string = re.escape(string)
        regex_str = r'\b%s\b' % string
        regex = re.compile(regex_str, re.I) if ignore_case else re.compile(regex_str)
        match = [x for x in self.dataset if regex.search(x)]
        if not match:
            return []
        return [str(x) for x in np.random.choice(match, min(len(match), n), replace=False)]

    def common_synonyms(self, n=30):
        ret = []
        allz = self.most_common(n=n, by_pos=True)
        allz = allz['VERB'] + allz['NOUN'] + allz['ADJ'] + allz['ADV'] + allz['ADP']
        for x in allz:
            if not x:
                continue
            sentences = self.search(x, ignore_case=False)
            try:
                syns = self.editor.synonyms(sentences, x, threshold=8)
            except:
                continue
            if syns:
                ret.append((x, syns))
        return ret

    def common_antonyms(self, n=30):
        ret = []
        allz = self.most_common(n=n, by_pos=True)
        allz = allz['VERB'] + allz['NOUN'] + allz['ADJ'] + allz['ADV'] + allz['ADP']
        for x in allz:
            if not x:
                continue
            sentences = self.search(x, ignore_case=False)
            try:
                syns = self.editor.antonyms(sentences, x, threshold=8)
            except:
                continue
            if syns:
                ret.append((x, syns))
        return ret

    def with_person(self, n=3):
        has_person = lambda y: any([x[0].ent_type_ == 'PERSON' for x in y.ents])
        pp = [x for x in self.parsed if has_person(x)]
        if not pp:
            return []
        ix = np.random.choice(len(pp), n)
        return [self.parsed[i].text for i in ix]

    def with_loc(self, n=3):
        has_person = lambda y: any([x[0].ent_type_ == 'GPE' for x in y.ents])
        pp = [x for x in self.parsed if has_person(x)]
        if not pp:
            return []
        ix = np.random.choice(len(pp), n)
        return [self.parsed[i].text for i in ix]

    def with_fairness(self, n=3):
        rel_words = set(['Christianity', 'Christian', 'priest', 'church', 'Bible', 'God', 'Jesus', 'Christ', 'Jesus Christ'
            'Protestantism', 'Protestant', 'pastor', 'church', 'Bible'
            'Roman Catholicism', 'Catholic', 'priest', 'church', 'Bible', 'Pope'
            'Eastern Orthodoxy', 'Orthodox', 'priest', 'church', 'Bible',
            'Anglicanism', 'Anglican'
            'Judaism', 'Jew', 'rabbi', 'synagogue', 'Torah',  'Moses', 'Abraham', 'Elijah', 'Isaiah', 'Jacob', 'Israel', 'Isaac',
            'Islam', 'Muslim', 'mullah', 'mosque', 'Quran', 'Allah', 'Mohammed', 'Muhammad', 'Ali', 'Abu Bakr', 'Umar', 'Uthman',
            'Hinduism', 'Hindu', 'pujari', 'temple', 'Vedas', 'Shiva', 'Vishnu', 'Ganesha', 'Durga', 'Saraswati', 'Kali', 'Lakshmi', 'Krishna', 'Brahma',
            'Buddhism', 'Buddhist', 'monk', 'temple', 'Tripitakas', 'Buddha', 'Gautama','Siddhartha Gautama', 'Siddhartha', 'the Dalai Lama', 'atheist', 'Atheist'])
        other = ['asian', 'hispanic', 'black man', 'black woman', 'white man', 'white woman', 'gay', 'homosexual', 'bisexual', 'trans', 'heterosexual']
        all_words = list(rel_words) + other
        return self.search(all_words)

    def with_temporal(self, n=3):
        words = ['before', 'after', 'tomorrow', 'yesterday', 'month', 'day', 'year', 'days ago', 'soon', 'early', 'earlier', 'later', 'late']
        return self.search(words)
    def with_negation(self, n=3):
        match = [x for x in self.dataset if find_neg(x)]
        if not match:
            return []
        return [str(x) for x in np.random.choice(match, 3)]

    def with_coref(self, n=3):
        words = ['he', 'she', 'it', 'them', 'they', 'hers', 'her', 'his', 'their', 'theirs', 'former', 'latter']
        return self.search(words)
