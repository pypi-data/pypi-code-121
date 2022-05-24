#!/usr/bin/python
# -*- coding: utf-8 -*-
#########################################################
## Thai Language Toolkit : version  1.5.5
## Chulalongkorn University
## written by Wirote Aroonmanakun
## Implemented :
##      upgrade to gensim 4.0
##      Corpus_build(DIR), W2V_train(Corpus), D2V_train(Corpus)
##      download_TNCw2v(), download_TNC3g()
##      TNC_load(), TNC3g_load(), trigram_load(Filename), unigram(w1), bigram(w1,w2), trigram(w1,w2,w3)
##      collocates(w,SPAN,STAT,DIR,LIMIT, MINFQ) = [wa,wb,wc]
##      w2v_exist(w), similar_words(w), similarlity(w1,w2), outofgroup(WORDLST), analogy(w1,w2,w3) 
#########################################################

import re
import os
import math
from collections import defaultdict
from operator import itemgetter
import requests

import gensim
from gensim.models import Word2Vec, KeyedVectors
from gensim.models.doc2vec import Doc2Vec, TaggedDocument

import pickle
from sklearn.decomposition import PCA
try:
    import matplotlib
    from matplotlib import pyplot
except ImportError:
    mplAvailable = False
else:
    mplAvailable = True
import numpy

import tltk
from tltk import nlp

#import gensim, logging
#logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

def download_TNCw2v():
    url = 'https://www.arts.chula.ac.th/ling/wp-content/uploads/TNC5cmodel2.bin'
    r = requests.get(url, allow_redirects=True)
    open(ATA_PATH +'/TNC5cmodel2.bin','wb').write(r.content)
    return()

def download_TNC3g(): 
    url = 'https://www.arts.chula.ac.th/ling/wp-content/uploads/TNC.3g'
    r = requests.get(url, allow_redirects=True)
    open(ATA_PATH +'/TNC.3g','wb').write(r.content)
    return()

def download_TNCd2v():
    url = 'https://www.arts.chula.ac.th/ling/wp-content/uploads/TNCd2v.bin'
    r = requests.get(url, allow_redirects=True)
    open(ATA_PATH +'/TNCd2v.bin','wb').write(r.content)
    return()

def TNC3g_load():
    global TriCount
    global BiCount
    global BiCount2
    global UniCount
    global TotalWord

    TriCount = defaultdict(int)
    BiCount = defaultdict(int)
    UniCount = defaultdict(int)
    BiCount2 = defaultdict(int)
    TotalWord = 0

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try: 
        fileObject = open(ATA_PATH + '/TNC3g','rb')
    except IOError:
        fileObject = open('TNC3g','rb') 
    TriCount = pickle.load(fileObject)

    for (w1,w2,w3) in TriCount:
        freq = int(TriCount[(w1,w2,w3)])
        BiCount[(w1,w2)] += freq
        UniCount[w1] += freq
        BiCount2[(w1,w3)] += freq
        TotalWord += freq
    return(1)



def TNC_load():
    global TriCount
    global BiCount
    global BiCount2
    global UniCount
    global TotalWord
    
    TriCount = defaultdict(int)
    BiCount = defaultdict(int)
    UniCount = defaultdict(int)
    BiCount2 = defaultdict(int)
    TotalWord = 0

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try: 
        InFile = open(ATA_PATH + '/TNC.3g','r',encoding='utf8')
    except IOError:
        InFile = open('TNC.3g','r',encoding='utf8')        
#    Filename = ATA_PATH + '/TNC.3g'
#    InFile = open(Filename,'r',encoding='utf8')
    for line in InFile:
        line.rstrip()
        (w1,w2,w3,fq) = line.split('\t')
        freq = int(fq)
        TriCount[(w1,w2,w3)] = freq
        BiCount[(w1,w2)] += freq
        UniCount[w1] += freq
        BiCount2[(w1,w3)] += freq
        TotalWord += freq
    return(1)

#### load a trigram file
def trigram_load(Filename):
    global TriCount
    global BiCount
    global BiCount2
    global UniCount
    global TotalWord
    
    TriCount = defaultdict(int)
    BiCount = defaultdict(int)
    UniCount = defaultdict(int)
    BiCount2 = defaultdict(int)
    TotalWord = 0

    InFile = open(Filename,'r',encoding='utf8')
    for line in InFile:
        line.rstrip()
        (w1,w2,w3,fq) = line.split('\t')
        freq = int(fq)
        TriCount[(w1,w2,w3)] = freq
        BiCount[(w1,w2)] += freq
        UniCount[w1] += freq
        BiCount2[(w1,w3)] += freq
        TotalWord += freq
    return(1)
    

#### return bigram in per million 
def unigram(w1):
    global UniCount
    global TotalWord
    
    if w1 in UniCount:
        return(float(UniCount[w1] * 1000000 / TotalWord))
    else:
        return(0)

#### return bigram in per million 
def bigram(w1,w2):
    global BiCount
    global TotalWord
    
    try:
      BiCount
    except NameError:
      TNC_load()

    if (w1,w2) in BiCount:
        return(float(BiCount[(w1,w2)] * 1000000 / TotalWord))
    else:
        return(0)
    
#### return trigram in per million 
def trigram(w1,w2,w3):
    global TriCount
    global TotalWord
    
    if (w1,w2,w3) in TriCount:
        return(float(TriCount[(w1,w2,w3)] * 1000000 / TotalWord))
    else:
        return(0)

##################################################        
##### Find Collocate of w1,  stat = {mi, chi2, freq}  direct = {left, right, both}  span = {1,2}
#### return dictionary colloc{ (w1,w2) : value }
def collocates(w,stat="chi2",direct="both",span=2,limit=10,minfq=1):
    global BiCount
    global BiCount2
    global TotalWord
    
    colloc = defaultdict(float)
    colloc.clear()
    
    if stat != 'mi' and stat != 'chi2':
        stat = 'freq' 
    if span != 2:
        span = 1 
    if direct != 'left' and direct != 'right':
        direct = 'both'
        
    if span == 1:    
        if direct == 'right' or direct == 'both':
            for w2 in [ key[1] for key in BiCount.keys() if key[0] == w]:
                if BiCount[(w,w2)] >= minfq:
                    colloc[(w,w2)] = compute_colloc(stat,w,w2)
        if direct == 'left' or direct == 'both':
            for w1 in [ key[0] for key in BiCount.keys() if key[1] == w]:
                if BiCount[(w1,w)] >= minfq:
                    colloc[(w1,w)] = compute_colloc(stat,w1,w)
    elif span == 2:
        if direct == 'right' or direct == 'both':
            for w2 in [ key[1] for key in BiCount.keys() if key[0] == w]:
                if BiCount[(w,w2)] >= minfq:
                    colloc[(w,w2)] = compute_colloc(stat,w,w2)
        if direct == 'left' or direct == 'both':
            for w1 in [ key[0] for key in BiCount.keys() if key[1] == w]:
                if BiCount[(w1,w)] >= minfq:
                    colloc[(w1,w)] = compute_colloc(stat,w1,w)
        if direct == 'right' or direct == 'both':
            for w2 in [ key[1] for key in BiCount2.keys() if key[0] == w]:
                if BiCount2[(w,w2)] >= minfq:
                    colloc[(w,w2)] = compute_colloc2(stat,w,w2)
        if direct == 'left' or direct == 'both':
            for w1 in [ key[0] for key in BiCount2.keys() if key[1] == w]:
                if BiCount2[(w1,w)] >= minfq:
                    colloc[(w1,w)] = compute_colloc2(stat,w1,w)
                
    return(sorted(colloc.items(), key=itemgetter(1), reverse=True)[:limit])
    
#    return(colloc)

##########################################
# Compute Collocation Strength between w1,w2  use bigram distance 2  [w1 - x - w2]
# stat = chi2 | mi | freq
##########################################
def compute_colloc2(stat,w1,w2):
    global BiCount2
    global UniCount
    global TotalWord

    bict = BiCount2[(w1,w2)]
    ctw1 = UniCount[w1]
    ctw2 = UniCount[w2]
    total = TotalWord
    
    if bict < 1 or ctw1 < 1 or ctw2 < 1:
        bict +=1
        ctw1 +=1
        ctw2 +=1 
        total +=2
    
###########################
##  Mutual Information
###########################
    if stat == "mi":
        mi = float(bict * total) / float((ctw1 * ctw2))
        value = math.log(mi,2)
#########################
### Compute Chisquare
##########################
    if stat == "chi2":
        value=0
        O11 = bict
        O21 = ctw2 - bict
        O12 = ctw1 - bict
        O22 = total - ctw1 - ctw2 +  bict
        value = float(total * (O11*O22 - O12 * O21)**2) / float((O11+O12)*(O11+O21)*(O12+O22)*(O21+O22))
#########################
### Compute Frequency (per million)
##########################
    if stat == 'freq':
        value = float(bict * 1000000 / total)
        
    return(value)


##########################################
# Compute Collocation Strength between w1,w2  use bigram distance 1  [w1 - w2]
# stat = chi2 | mi | ll
##########################################
def compute_colloc(stat,w1,w2):
    global BiCount
    global UniCount
    global TotalWord


    bict = BiCount[(w1,w2)]
    ctw1 = UniCount[w1]
    ctw2 = UniCount[w2]
    total = TotalWord
    

    if bict < 1 or ctw1 < 1 or ctw2 < 1:
        bict +=1
        ctw1 +=1
        ctw2 +=1 
        total +=2
    
###########################
##  Mutual Information
###########################
    if stat == "mi":
        mi = float(bict * total) / float((ctw1 * ctw2))
        value = math.log(mi,2)
#########################
### Compute Chisquare
##########################
    if stat == "chi2":
        value=0
        O11 = bict
        O21 = ctw2 - bict
        O12 = ctw1 - bict
        O22 = total - ctw1 - ctw2 +  bict
        value = float(total * (O11*O22 - O12 * O21)**2) / float((O11+O12)*(O11+O21)*(O12+O22)*(O21+O22))
#########################
### Compute Frequency (per million)
##########################
    if stat == 'freq':
        value = float(bict * 1000000 / total)
        
    return(value)

#######################################################################
### Load Corpus from text files in a directory
def Corpus_build(dir, sep="file", lang="th",stopword="y", filetype="txt"):
    ThaiStopwords = ['ที่','การ','เป็น','ใน','ของ','มี','และ','ได้','ให้','ว่า','ไป','มา','ก็','ๆ','ความ','กับ','หรือ','อยู่','กัน','จาก','นี้','แต่','อย่าง','ด้วย','เขา','ขึ้น','นั้น','ผู้','ซึ่ง','ตาม','โดย','ยัง','เพื่อ','อีก','เมื่อ','ถึง','เพราะ','ออก','คือ','จึง','กว่า','ไว้','ถ้า','อะไร','ลง','แบบ','ทุก','อื่น','เช่น','น่า','สามารถ','แห่ง','นี่','ใคร','ใด','เอง','จะ','คง','เคย','อาจ','ต้อง','แล้ว','ครับ','คะ','ค่ะ','นะ','ไม่','ไม่ได้']
    text_corpus = []
#    count = defaultdict(int)

    rootDir = dir

    for dirName, subdirList, fileList in os.walk(rootDir):
        for fname in sorted(fileList):
            if not fname.endswith('.'+filetype):
                continue
            with open(dirName + '/' + fname,encoding='utf8') as f:
                if sep == 'edu':
                    txt = f.read()
                    doc = nlp.segment(txt)
                    doc = doc.replace('<s/>','')
                    doc = doc.replace('\n','')
                    for u in doc.split('<u/>'):
                        wrdlst = re.split("[, |?:!\^]+",u)
                        if '' in wrdlst : wrdlst.remove('')
                        if wrdlst != []:
                            if lang =='th' and stopword == 'y':
                                wrdlst_wo_sw = [w for w in wrdlst if not w in ThaiStopwords]
                                text_corpus.append(wrdlst_wo_sw) 
                            else:
                                text_corpus.append(wrdlst) 
                elif sep == 'file':
                    txt = f.read()
                    doc = nlp.word_segment(txt)
#                    doc = ' '.join(lines)
                    doc = doc.replace('<s/>','')
                    doc = doc.replace('\n','')
                    wrdlst = re.split("[, |?:!\^]+",doc)
                    if '' in wrdlst : wrdlst.remove('')
                    if wrdlst != []:
                        if lang =='th' and stopword == 'y':
                            wrdlst_wo_sw = [w for w in wrdlst if not w in ThaiStopwords]
                            text_corpus.append(wrdlst_wo_sw) 
                        else:
                            text_corpus.append(wrdlst) 
                else:
                    for line in f.readlines():
                        doc = nlp.word_segment(line)
                        doc = doc.replace('\n','')
                        doc = doc.replace('<s/>','')
                        wrdlst = re.split("[, |?:!\^]+",doc)
                        if '' in wrdlst : wrdlst.remove('')
                        if wrdlst != []:
                            if lang=='th' and stopword == 'y':
                                wrdlst_wo_sw = [w for w in wrdlst if not w in ThaiStopwords]
                                text_corpus.append(wrdlst_wo_sw) 
                            else:
                                text_corpus.append(wrdlst) 
    return(text_corpus)

def D2V_train(text_corpus):
    documents = [TaggedDocument(doc, [i]) for i, doc in enumerate(text_corpus)]
    #  building a model
    model = Doc2Vec(vector_size=100, min_count=2, dm =1, epochs=30)
    model.build_vocab(documents)
    model.train(documents, total_examples=model.corpus_count, epochs=model.epochs)
    return(model)

def W2V_train(corpus, min=5):                       
    model = Word2Vec(corpus,min_count=min)
    return(model)
#    model.save(outmodel+'.bin')

## convert corpus data into word list data with frequency
# if data is pos tagged  word_tag will be counted as one token        
class Corpus:
    def frequency(self,corpus):
        word = {}
        for line in corpus:
            for w in line:
                if w in word:
                    word[w] +=1
                else:
                    word[w] =1
        return(word)
    def dispersion(self,corpus):
        word = {}
        for line in corpus:
            for w in list(set(line)):
                if w in word:
                    word[w] +=1
                else:
                    word[w] =1
        return(word)
    def totalword(self,corpus):
        total = 0
        for line in corpus:
            total += len(line)
        return(total)

## create object for comparing two word frequency lists
class Xwordlist:
    def intersect(self,A,B):
        X = A.keys()
        Y = B.keys()
        return([value for value in X if value in Y])
    def onlyA(self,A,B):
        X = A.keys()
        Y = B.keys()
        return([value for value in X if value not in Y])
    def onlyB(self,A,B):
        X = A.keys()
        Y = B.keys()
        return([value for value in Y if value not in X])
    def union(self,A,B):
        X = A.keys()
        Y = B.keys()
        return(list(set(X)|set(Y))) 



'''
############ load D2V model from TNC
def D2V_load(File="TNCd2v.bin"):
    global d2v_model

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try:
        d2v_model = Doc2Vec.load(File,'rb')
    except IOError:
        d2v_model = Doc2Vec.load(ATA_PATH +'/' +"TNCd2v.bin",'rb')
    return(1)  

def similar_edu(seg,n=1):
    global d2v_model

    x = seg.split('|')
    #create vector for that segment
    newvect = d2v_model.infer_vector(x)
    #find the most similar top 10 vectors
    sims = d2v_model.dv.most_similar([newvect])
    if n == 1:
        return(pars[int(sims[0][0])])
    else:
        ct = 0
        result = []
        while ct < n:
            result.append(pars[int(sims[0][ct])])
            ct += 1
        return(result)    
    #print using index [0][0], [0][1]
#    print('1.',pars[int(sims[0][0])])
#    print('2.',pars[int(sims[0][1])])

'''

#######################################################################
#### word2vec model created from TNC 3.0 gensim 4.0

def W2V_load(File="TNCc5model2.bin"):
    global w2v_model

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try:
        w2v_model = Word2Vec.load(File,'rb')
    except IOError:
        w2v_model = Word2Vec.load(ATA_PATH +'/' +"TNCc5model2.bin",'rb')
    return(1)    

def w2v_load():
    global w2v_model

    path = os.path.abspath(__file__)
    ATA_PATH = os.path.dirname(path)
    try:
        w2v_model = Word2Vec.load(ATA_PATH +'/' +"TNCc5model2.bin",'rb')
    except IOError:
        w2v_model = Word2Vec.load("TNCc5model2.bin",'rb')
    return(1)

def w2v_exist(w):
    global w2v_model
    try:
      w2v_model
    except NameError:
      w2v_load()
#    if w in list(w2v_model.wv.vocab):
    if w in list(w2v_model.wv.index_to_key):
        return(True)
    else:
        return(False)
    
def w2v(w):
#    if w in list(w2v_model.wv.vocab):
    if w in list(w2v_model.wv.index_to_key):
        return(w2v_model.wv[w])
    else:
        return()
    
def similarity(w1,w2):
    global w2v_model
    degree = ''
    vocabs = list(w2v_model.wv.index_to_key)
    if w1 in vocabs and w2 in vocabs:
        degree = w2v_model.wv.similarity(w1,w2)
    else:
        degree = 0.    
    return(degree)

def cosine_similarity(w1,w2):
    global w2v_model
    degree = ''
    vocabs = list(w2v_model.wv.index_to_key)
    if w1 in vocabs and w2 in vocabs:
        degree = cosine_similarity = numpy.dot(w2v_model.wv[w1], w2v_model.wv[w2])/(numpy.linalg.norm(w2v_model.wv[w1])* numpy.linalg.norm(w2v_model.wv[w2]))
    else:
        degree = 0.    
    return(degree)


def similar_words(w1,n=10,cutoff=0.,score="n"):
    global w2v_model                
    if w1 in list(w2v_model.wv.index_to_key):
        out = w2v_model.wv.most_similar(w1)
        result = []
        ct = 0
        for (w,p) in out:
            if p > cutoff and ct < n:
                if score == 'n':
                    result.append(w)
                else:
                    result.append((w,p))
                ct += 1
    return(result)

def outofgroup(wrdlst):
    global w2v_model
    wrdlst1 = []
    try:
      w2v_model
    except NameError:
      w2v_load()
    vocabs = list(w2v_model.wv.index_to_key)
    for w in wrdlst:
        if w in vocabs:
            wrdlst1.append(w)
    out = w2v_model.wv.doesnt_match(wrdlst1)
    return(out)

def w2v_diffplot(ww,wx,wy):
    global w2v_model
    try:
      w2v_model
    except NameError:
      w2v_load()
    font = {'family' : 'TH Sarabun New',
        'weight' : 'bold',
        'size'   : 14}
    matplotlib.rc('font', **font)
    xs = list(range(1,101))
    ys = w2v_model.wv[ww] - w2v_model.wv[wx]
    pyplot.plot(xs,ys,label=ww+'-'+wx)
    ys = w2v_model.wv[ww] - w2v_model.wv[wy]
    pyplot.plot(xs,ys,label=ww+'-'+wy)
    pyplot.legend()
    pyplot.show()
    return(1)

def w2v_dimplot(wrdlst):
    global w2v_model
    wrdlst1=[]
    try:
      w2v_model
    except NameError:
      w2v_load()
    vocabs = list(w2v_model.wv.index_to_key)
    for w in wrdlst:
        if w in vocabs:
            wrdlst1.append(w)
    font = {'family' : 'TH Sarabun New',
        'weight' : 'bold',
        'size'   : 14}
    matplotlib.rc('font', **font)
    xs = list(range(1,101))
    for i, word in enumerate(wrdlst1):
        ys = w2v_model.wv[word]
        pyplot.plot(xs,ys,label=word)
    pyplot.legend()
    pyplot.show()
    return(1)
    

def w2v_plot(wrdlst):
    global w2v_model
    wrdlst1=[]
    try:
      w2v_model
    except NameError:
      w2v_load()
    vocabs = list(w2v_model.wv.index_to_key)
    for w in wrdlst:
        if w in vocabs:
            wrdlst1.append(w)
    # fit a 2d PCA model to the vectors
    font = {'family' : 'TH Sarabun New',
        'weight' : 'bold',
        'size'   : 14}
    matplotlib.rc('font', **font)

    X = w2v_model.wv[wrdlst1]
    pca = PCA(n_components=2)
    result = pca.fit_transform(X)
    # create a scatter plot of the projection
    ax = pyplot.axes()
    pyplot.scatter(result[:, 0], result[:, 1])
    for i, word in enumerate(wrdlst1):
        pyplot.annotate(word, xy=(result[i, 0], result[i, 1]))
        ax.arrow(0, 0, result[i, 0], result[i, 1], head_width=0.05, head_length=0.1)
    pyplot.show()
    return(1)

    
###  man1 : king2  woman3 : queen
def analogy(w1,w2,w3, n=1):   #king - man + woman = queen    
    global w2v_model
    try:
      w2v_model
    except NameError:
      w2v_load()
    vocabs = list(w2v_model.wv.index_to_key)
    if w1 in vocabs and w2 in vocabs and w3 in vocabs:    
        return(w2v_model.wv.most_similar(positive=[w3, w2], negative=[w1], topn=n))
    else:
        return([])

#### codes adapted from http://chrisculy.net/lx/wordvectors/wvecs_visualization.html
def w2v_compare_color(wds):
    global w2v_model
    wdsr = wds[:]
    wdsr.reverse()

    font = {'family' : 'TH Sarabun New',
        'weight' : 'bold',
        'size'   : 14}
    matplotlib.rc('font', **font)
    
#    display(HTML('<b>Word vectors for: %s</b>' % ', '.join(wdsr)))
    
    vs = [w2v_model.wv[wd] for wd in wds]
    dim = len(vs[0])
    
    fig = pyplot.figure(num=None, figsize=(12, 2), dpi=80, facecolor='w', edgecolor='k')
    ax = fig.add_subplot(111)
    ax.set_facecolor('gray')
    
    for i,v in enumerate(vs):
        ax.scatter(range(dim),[i]*dim, c=vs[i], cmap='Spectral', s=16)
    
    #plt.xticks(range(n), [i+1 for i in range(n)])
    pyplot.xlabel('Dimension')
    pyplot.yticks(range(len(wds)), wds)
    
    pyplot.show()        

############ END OF GENERAL MODULES ##########################################################################





## testing area
'''
pars = Corpus_build('/Users/macbook/Cloud/Dropbox/Corpus/corpora/ThaiNews',sep="edu",filetype="txt")
print(pars[0:3])

#train Doc2Vec model
model = D2V_train(pars)


#a new paragraph
x = 'การ|ทดลอง|ภาค|สนาม|โดย|ทีม|ผู้|เชี่ยวชาญ|เรื่อง|การ|ให้|และ|การ|ช่วยเหลือ|ผู้|อื่น'.split('|')
#create vector for that paragraph
newvect = model.infer_vector(x)
#find the most similar top 10 vectors
sims = model.dv.most_similar([newvect])
print(sims)
#print using index [0][0], [0][1]
print('1.',pars[int(sims[0][0])])
print('2.',pars[int(sims[0][1])])


# read all .wsg files in the directory
pars = Corpus_build('/Users/macbook/Cloud/Dropbox/Corpus/Thaipublica/wsg',filetype="wsg")
print(pars[0:3])
x1 = Corpus()
print(x1.totalword(pars))
c1 = Corpus()
c2 = Corpus()
Xcomp = Xwordlist()
print(Xcomp.onlyA(c1.frequency(pars[:100]),c2.frequency(pars[101:])))

W2V_load('TNCc5model2.bin')
print(similar_words('ขบ'))

#w2v_load()
#w2v_plot("ผู้ชาย ผู้หญิง เก่ง ฉลาด สวย หล่อ".split(" "))
#w2v_compare_color("ผู้ชาย ผู้หญิง เก่ง ฉลาด สวย หล่อ".split(" "))
#w2v_plot(['เก็บรักษา', 'จัดเตรียม','เอา', 'รวบรวม', 'ซื้อ', 'สะสม'])
#w2v_diffplot("เล็กน้อย","เล็ก", "น้อย")
#w2v_plot(["แทรกซ้อน","แทรก", "ซ้อน"])
'''