from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel

import os
import logging, sys
import datetime


def find_similar(tfidf_matrix, index, top_n=5):
    cosine_similarities = linear_kernel(tfidf_matrix[index:index + 1], tfidf_matrix).flatten()
    related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] if i != index]
    # related_docs_indices = [i for i in cosine_similarities.argsort()[::-1] ]
    return [(index, cosine_similarities[index]) for index in related_docs_indices][0:top_n]


def findMisclassification(df, classField):
    start_time = datetime.datetime.now()
    # newCol ='Desp_NoSign_ShortDescription'
    newCol = 'content'
    tfidf = TfidfVectorizer().fit_transform(df[newCol].values.astype('U'))
    similarList = []
    n = len(df[newCol])
    threshold = 0.95 #config.qualityControl['simiScore']
    count = 0
    for searchIndex in range(n):
        simiIndex = set()
        for index, score in find_similar(tfidf, searchIndex):
            if (score > threshold):
                if df[classField][searchIndex] != df[classField][index]:
                    simiIndex.add(df['TicketId'][index])
        if simiIndex:
            simiIndex.add(df['TicketId'][searchIndex])
            if simiIndex not in similarList:
                if similarList:
                    newSet = True
                    for itemSimi in simiIndex:
                        # for itemList in similarList:
                        for i in range(len(similarList)):
                            if itemSimi in similarList[i]:
                                similarList[i] = set(list(similarList[i]) + list(simiIndex))
                                newSet = False
                                break
                    # that mean simiIndex is new set
                    if newSet:
                        if not set(simiIndex) < set(similarListSet):
                            similarList.append((set(simiIndex)))
                else:
                    similarListSet = (tuple(x) for x in similarList)
                    if not set(simiIndex) < set(similarListSet):  # check subset of list
                        similarList.append(set(simiIndex))
        if (searchIndex % 1000 == 0 and searchIndex != 0):
            #logger.info('Compared %s data', (str)(searchIndex))
            print("Compared %s data", str(searchIndex))

        count = count + 1
    end_time = datetime.datetime.now()

    #logger.info('----Time to find miss classification {}----'.format(end_time - start_time))
    print('Time to find miss classiication {}----'.format(end_time - start_time))
    return similarList
