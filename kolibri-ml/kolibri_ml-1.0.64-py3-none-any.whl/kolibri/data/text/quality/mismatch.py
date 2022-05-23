import os

import numpy as np
import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

from cosineSimilarity import findMisclassification

###Load data

corpus =pd.read_excel("../octaplus_translated_V4.xlsx")
corpus = corpus[corpus['ToKeep'] == True]
bytag = corpus.groupby('Libelle').aggregate(np.count_nonzero)
tags = bytag[bytag.Group > 20].index

corpus['Libelle'] = np.where(corpus['Libelle'].isin(tags), corpus['Libelle'], 'OTHER')
    
corpus["content"]=corpus['translated_title_fr'].fillna('') + "\n"+corpus['translated_clean_body_fr'].fillna('')  ###!!!! different from above --> https://stackoverflow.com/questions/33158417/pandas-combine-two-strings-ignore-nan-values
    #corpus.dropna(subset=["content"], inplace=True)
corpus["TicketId"] =  ['email_'+ str(i).zfill(5) for i in range(0,corpus.shape[0])]
corpus.reset_index(inplace=True)

ticketIdsGroup = findMisclassification(corpus, 'Libelle')
