# -*- coding: utf-8 -*-

# Created on Fri Jun 18 09:19:53 2021


import os
import nltk
import gensim
import re
import string
import wordcloud
import xml.etree.ElementTree as ET
from nltk.tokenize import word_tokenize
from gensim.corpora.dictionary import Dictionary
from nltk.stem import WordNetLemmatizer, SnowballStemmer
import matplotlib.pyplot as plt
# nltk.download('averaged_perceptron_tagger')
rootPath = r"C:\Users\79988\Desktop\文本分析项目\XMLcollection1"
resultPath = r"C:\Users\79988\Desktop\文本分析项目\ForTest"
xml_papers = os.listdir(rootPath)
judgeShort=1


if "desktop.ini" in xml_papers:
    xml_papers.remove("desktop.ini")  # removing the hidden 'desktop.ini' which will cause issue

# A dictionary that will contain the PMC IDs as keys and texts of articles sections as value:
# docs = dict.fromkeys(xml_papers)

# will contain articles after parsing
articles = [[] for i in range(len(xml_papers))]

# A dictionary that will contain section types of the articles

Important_sections = ['ABSTRACT', 'INTRO', 'METHODS', 'DISCUSS', 'RESULTS', 'CASE', 'CONCL', 'ABBR', 'FIG', 'TABLE']
Other_sections = ['SUPPL', 'REF', 'APPENDIX', 'AUTH_CONT', 'ACK_FUND', 'COMP_INT', 'REVIEW_INFO']

stpwrd = nltk.corpus.stopwords.words('english')

# Adding new stop words to the list of stop words:
new_stopwords = ["surname", "ref", "abstract", "intro", "http", 'left upper', 'right upper', 'article',
                 'published', 'even though', 'paragraph', 'page', 'sentence', 'et', 'al', 'etc','province','would','today',]
stpwrd.extend(new_stopwords)

# Parsing the XML files and getting its root
xml_papersw=[]
##############################################################
##############################################################
for k, article in enumerate(xml_papers):
    modified_path = os.path.join(rootPath, article)
    temp = ET.parse(modified_path, ET.XMLParser(encoding='utf-8'))
    articles[k].append(temp)
    # print(temp)
    collection = temp.getroot()
    for i, document in enumerate(collection):
        judgeShort = 0
        for x in document.findall("passage"):
            for inf in x.findall('infon'):
                if inf.attrib == {'key': 'section_type'}:
                    if inf.text not in Other_sections:
                        if inf.text in ['ABSTRACT', 'CONCL','METHODS','RESULTS']:
                            judgeShort=1
    list_i = list(xml_papers[k])  # str -> list
    list_i.insert(10, str(judgeShort))  # 注意不用重新赋值
    xml_papersw1= ''.join(list_i)
    xml_papersw.append(xml_papersw1)
#############################################################
############################################################
docs = dict.fromkeys(xml_papersw)
section_types = dict.fromkeys(xml_papersw)

for k, article in enumerate(xml_papers):
    modified_path = os.path.join(rootPath, article)
    temp= ET.parse(modified_path, ET.XMLParser(encoding='utf-8'))
    articles[k].append(temp)
    # print(temp)
    collection = temp.getroot()
    section_types[xml_papersw[k]] = []
    docs[xml_papersw[k]] = []
    # Extracting all the texts of all sections
    for i, document in enumerate(collection):
        judgeShort = 0
        for x in document.findall("passage"):
            # print(x.findall('infon'))
            infon_list = x.findall('infon')

            # Removing footnote and table contents sections:
            if any(inf.text == 'footnote' for inf in infon_list) or any(inf.text == 'table' for inf in infon_list):
                document.remove(x)
    for x in document.findall("passage"):
            for inf in x.findall('infon'):
                if inf.attrib == {'key': 'section_type'}:
                    section_types[xml_papersw[k]].append(inf.text)
                    if inf.text not in Other_sections:
                        temp1 = getattr(x.find('text'), 'text', None)
                        if inf.text in ['ABSTRACT', 'CONCL']:
                            docs[xml_papersw[k]].append(temp1 + " " + temp1)
                        else:
                            docs[xml_papersw[k]].append(temp1)

    docs[xml_papersw[k]] = list(filter(None, docs[xml_papersw[k]]))

# list(docs.keys()).index('PMC7084952.xml')

# joining texts of each article into one string.
docs_list = [' '.join(docs.get(doc)) for doc in docs]

# removing whitespace
data = [re.sub(r'\s', ' ', doc) for doc in docs_list]

# removing urls:
# https:\/\/www\.\w+\.\w+
data = [re.sub(r'(https|http)?:\/\/(\w|\.|\/|\?|\=|\&|\%)*\b', ' ', doc) for doc in data]
# removing numbers
# r'[\s\(][^-a-zA-Z]+\-*[\d\.]+'
data = [re.sub(r'[\s\(][^-a-zA-Z]+\-*[^-a-zA-Z]+', ' ', doc) for doc in data]

# Adding 2019 to -nCoV:
data = [re.sub(r'-nCoV', '2019-nCoV', doc) for doc in data]

# Removing medical units:
data = [re.sub(r'[a-zA-Z]+\/[a-zA-Z]+', '', doc) for doc in data]

# Removing white spaces again
data = [re.sub(r'\s', ' ', doc) for doc in data]

# removing punctuations:
# removing '-' from punctuations list.
puncs = re.sub('-', '', string.punctuation)
data = [re.sub(r'[{}]+'.format(puncs), '', doc) for doc in data]

# lowering new line capital words except those which contain digits:
pattern = r'[A-Z]{1}[a-z]{2,}\s'  # Defined pattern for finding capital words except those which contain digits

for i, doc in enumerate(data):
    index_temp = [(m.start(0), m.end(0)) for m in re.finditer(pattern, doc)]
    for ind in index_temp:
        ii = ind[0]
        jj = ind[1]


        data[i] = data[i].replace(data[i][ii:jj], data[i][ii:jj].lower())
# =============================================================================


stemmer = SnowballStemmer("english")
wnl = WordNetLemmatizer()


# A function for lemmatizing and stemming a text
def lemmatize_stemming(text):
    return stemmer.stem(wnl.lemmatize(text, pos='v'))


# A token preprocessing function
def preprocess(text):
    result = []
    mydict = {}  # A dictionary which will contain original tokens before lemmatizing and stemming
    for token in word_tokenize(text):
        # if token not in stpwrd and len(token) >= 3:
        if len(token) >= 2:
            temp = lemmatize_stemming(token)
            mydict[temp] = token
            result.append(temp)
    return result, mydict


mywords = []
# A dictionary which contains original tokens as value and lemmetized stemmized token as key:
token_word_dict = {}

for doc in data:
    data_new = []

    data_new=((doc).split(" "))
    tagged = nltk.pos_tag(data_new)
    data_new1 = []
    for word, pos in tagged:
        if pos != 'MD':
            data_new1.append(word)
    var = ' '.join(data_new1)
    mywords.append(preprocess(var)[0])
    token_word_dict.update(preprocess(var)[1])
            # print(preprocess(doc)[1])
# Removing words with frequency < 2:
# for sub in mywords:
#     sub[:] = [ele for ele in sub if sub.count(ele) > 1]

# Building the bigram models
bigram = gensim.models.phrases.Phrases(mywords, min_count=2, threshold=10)

# cearting list of bigrams:
mywords2 = bigram[mywords]

# Building the trigram models
trigram = gensim.models.phrases.Phrases(bigram[mywords], min_count=2, threshold=10)
mywords3 = trigram[mywords2]


# A function for removing stop words:
def remove_stopwrd(txt):
    result = []
    for wrd in txt:
        temp = wrd.split('_')
        if not any(ele in stpwrd for ele in temp):
            result.append(wrd)
    return result


mywords3_no_stopwrd = [[] for i in range(len(mywords3))]

mywords3_no_stopwrd = [remove_stopwrd(lis) for lis in mywords3]

# Create Dictionary of trigrams

dictionary_trigram = Dictionary(mywords3_no_stopwrd)

# Create Corpus
corpus_trigram= [dictionary_trigram.doc2bow(text) for text in mywords3_no_stopwrd]

# =============================================================================

tfidf_trigram_model = gensim.models.tfidfmodel.TfidfModel(corpus=corpus_trigram,
                                                          id2word=dictionary_trigram,
                                                          normalize=True)
def delete_repeat_max(txt):
    result = []
    for wrd in txt:
        if not(wrd.find(" ")):
            temp_wrd=wrd
            length=0
            temp_length = 0
            temp_word=""
            for wrd1 in txt:
                if wrd1.find(wrd):
                    length=len(wrd1)
                    if length>temp_length:
                        temp_length=length
            if not(temp_length==len(wrd)):
                return temp_length,wrd
            else:
                return 0

def delete_repeat(txt,intt,wrd2,txt1):
    result = []
    result=txt
    result1 = []
    result1 = txt1
    delete_sum=0
    for i,wrd in enumerate(txt):
        if wrd.find(wrd2):
            length=len(wrd)
            if length<intt:
                result.remove(wrd)
                result1[i]=""
    while "" in result1:
        result1.remove("")
        return result,result1




# Top 10 tokens
# tfidf_top10_words=[[] for i in range(len(corpus_trigram))]
top10_trigram_of_articles = [[] for i in range(len(corpus_trigram))]
top_trigram_of_articles = [[] for i in range(len(corpus_trigram))]
# Will contain the original words before being stemmized and lemmatized:
top10_tri_words_original = [[] for i in range(len(corpus_trigram))]
top10_tri_freqs = [[] for i in range(len(corpus_trigram))]
top10_tri_words_original2 = [[] for i in range(len(corpus_trigram))]
top10_tri_freqs2 = [[] for i in range(len(corpus_trigram))]
for i, corp in enumerate(corpus_trigram):
    temp3 = tfidf_trigram_model[corp]
    # print(temp3)
    wd = int(xml_papersw[i][10])
    ####################################
    temp_top_ori = sorted(temp3, key=lambda x: x[1], reverse=True)
    temp_top_wrds_ori = [dictionary_trigram.get(x[0]) for x in temp_top_ori]
    top_trigram = [' '.join(re.findall(r'[\w\-]+\_[\w\-]+[\_[\w\-]+]*', word)) for word in temp_top_wrds_ori]
    while ("" in top_trigram):
        top_trigram.remove("")
    temp4_top10words = [(dictionary_trigram.get(x[0]), x[1]) for x in temp_top_ori]
    # if wd==1:
    for m, n in temp4_top10words:
        if m in top_trigram:
            temp5 = m.split('_')
            temp6 = ''
            for ii, tex in enumerate(temp5):  # Rejoining the trigrams with '_' again
                temp6 = temp6 + token_word_dict.get(temp5[ii]) + ' '
                # print(temp6)
            top10_tri_words_original[i].append(temp6)
            top10_tri_freqs[i].append(n)
            # print(m,n, temp6)
        else:
            # tagged = nltk.pos_tag(token_word_dict.get(m))
            a = []
            a.append(token_word_dict.get(m))
            tagged = nltk.pos_tag(a)
            for word, pos in tagged:
                if pos!='JJ' and not(len(token_word_dict.get(m))<=3 and token_word_dict.get(m).islower()):
                    top10_tri_words_original[i].append(token_word_dict.get(m))
                    top10_tri_freqs[i].append(n)
        top10_tri_words_original[i] = top10_tri_words_original[i][:10]
        delete_repeat_max(top10_tri_words_original[i])[0]
        top10_tri_freqs[i] = top10_tri_freqs[i][:10]
    # else:
    #     for m, n in temp4_top10words:
    #         if m in top_trigram:
    #             temp5 = m.split('_')
    #             temp6 = ''
    #             for ii, tex in enumerate(temp5):  # Rejoining the trigrams with '_' again
    #                 temp6 = temp6 + token_word_dict.get(temp5[ii]) + ' '
    #                 # print(temp6)
    #             top10_tri_words_original2[i].append(temp6)
    #             top10_tri_freqs2[i].append(n)
    #             # print(m,n, temp6)
    #         else:
    #             # tagged = nltk.pos_tag(token_word_dict.get(m))
    #             a = []
    #             a.append(token_word_dict.get(m))
    #             tagged = nltk.pos_tag(a)
    #             for word, pos in tagged:
    #                 if pos!='JJ' and not(len(token_word_dict.get(m))<=3 and token_word_dict.get(m).islower()):
    #                     top10_tri_words_original2[i].append(token_word_dict.get(m))
    #                     top10_tri_freqs2[i].append(n)
    #         top10_tri_words_original2[i] = top10_tri_words_original2[i][:10]
    #         top10_tri_freqs2[i] = top10_tri_freqs2[i][:10]
        ##################################


### Plotting top 10 trigrams ###

i=90
# random.sample(range(0, len(xml_papers)), 30):
for i in range(len(corpus_trigram)):
    # plt.figure(figsize=(24, 22))  # width:20, height:3
    plt.bar(top10_tri_words_original[i], top10_tri_freqs[i])
    wd = int(xml_papersw[i][10])
    if wd==0:
        plt.title(f'The Short Article Top 10 trigrams "weighted" for {xml_papersw[i][:-5]}')
        plt.xticks(rotation=45, fontsize=11)

        # Saving the figures in result path:
        plt.savefig(os.path.join(resultPath, f'The Short Article Trigram_figure_{xml_papersw[i][:-5]}'), bbox_inches="tight")
        plt.close()

    if wd == 1:
        plt.title(f'The Regular Article Top 10 trigrams "weighted" for {xml_papersw[i][:-5]}')
        plt.xticks(rotation=45, fontsize=11)

        # Saving the figures in result path:
        plt.savefig(os.path.join(resultPath, f'The Regular Article Trigram_figure_{xml_papersw[i][:-5]}'), bbox_inches="tight")
        plt.close()

for i in range(len(corpus_trigram)):
    # plt.figure(figsize=(24, 22))  # width:20, height:3
    plt.bar(top10_tri_words_original[i], top10_tri_freqs[i])
    txt=""
    for i in range(10):
        num=int(top10_tri_freqs[i])
        for x in range(num):
            txt=top10_tri_words_original[i]+" "
    w = wordcloud.WordCloud(background_color="white")  # 把词云当做一个对象
    w.generate(txt)
    w.to_file(os.path.join(resultPath, f'The Short Article Trigram_figure_WorldCloud{xml_papersw[i][:-5]}'))
    wd = int(xml_papersw[i][10])
    if wd==0:
        plt.title(f'The Short Article Top 10 trigrams "weighted" for {xml_papersw[i][:-5]}')
        plt.xticks(rotation=45, fontsize=11)

        # Saving the figures in result path:
        plt.savefig(os.path.join(resultPath, f'The Short Article Trigram_figure_{xml_papersw[i][:-5]}'), bbox_inches="tight")
        plt.close()

    if wd == 1:
        plt.title(f'The Regular Article Top 10 trigrams "weighted" for {xml_papersw[i][:-5]}')
        plt.xticks(rotation=45, fontsize=11)

        # Saving the figures in result path:
        plt.savefig(os.path.join(resultPath, f'The Regular Article Trigram_figure_{xml_papersw[i][:-5]}'), bbox_inches="tight")
        plt.close()






































