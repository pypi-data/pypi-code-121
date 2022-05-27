import pandas as pd
from konlpy.tag import *
from collections import Counter
import numpy as np
from math import log
import copy
import operator
from numpy import dot
from numpy.linalg import norm

hannanum = Hannanum()
kkma = Kkma()
komoran = Komoran()

import hssh


class Document:

    def __init__(self, dataframe, analysis_by):
        self.dataframe = dataframe
        self.df = dataframe[analysis_by]
        self.num = len(self.df)
        words = []
        for paper in self.df:
            words = words.__add__(hannanum.nouns(paper))
        self.voca_dict = dict(Counter(words).most_common())
        self.voca_list = list(self.voca_dict.keys())
        self.idf_dict = self.idf()

    def idf(self):
        idf_dict = dict.fromkeys(self.voca_list, 0)
        for word in self.voca_list:
            cnt = 0
            for paper in self.df:
                if word in paper:
                    cnt += 1
            idf_dict[word] = log(len(self.df) / (1 + cnt))
        self.idf_dict = idf_dict
        return idf_dict

    def modify_voca(self, cut=1.5, *args):
        for word in self.voca_list:
            if self.idf_dict[word] < cut:
                print(word, end=' ')
                del self.voca_dict[word]
                del self.idf_dict[word]
                self.voca_list.remove(word)

    def keywords(self, title='제목', cut=2, *args):
        temp = {}
        for i in range(len(self.df)):
            paper = Paper(self.df[i], self)
            temp[self.dataframe[title].iloc[i]] = paper.keywords_f(cut)
        return temp

    def cos_sim(self, title='제목', *args):
        temp = np.zeros((len(self.df), len(self.df)))
        for i in range(len(self.df)):
            paper1 = Paper(self.df[i], self)
            for j in range(len(self.df)):
                paper2 = Paper(self.df[j], self)
                temp[i][j] = dot(paper1.tfidf, paper2.tfidf) / (norm(paper1.tfidf) * norm(paper2.tfidf))
            temp[i][i] = np.nan
        cos_sim_df = pd.DataFrame(temp, index=self.dataframe[title], columns=self.dataframe[title])
        return cos_sim_df


class Paper:

    def __init__(self, txt, document):
        self.txt = txt
        self.doc = document
        dtm = []
        for word in document.voca_list:
            dtm.append(txt.count(word))
        self.tf = np.array(dtm)
        idf = np.array(list(self.doc.idf_dict.values()))
        self.tfidf = self.tf * idf

    def keywords_f(self, cut=2, *args):
        tfidf_dict = {}
        for i in range(self.tfidf.size):
            if self.tfidf[i] > cut:
                tfidf_dict[self.doc.voca_list[i]] = self.tfidf[i]
        keywords = sorted(tfidf_dict.items(), key=operator.itemgetter(1), reverse=True)
        self.keywords = keywords
        return keywords

def notstring(DataFrame,analysis_by):
    for i in range(len(DataFrame[analysis_by])):
        text=DataFrame[analysis_by].iloc[i]
        if type(text) is not str:
            DataFrame[analysis_by].iloc[i]='0'
    return DataFrame
 