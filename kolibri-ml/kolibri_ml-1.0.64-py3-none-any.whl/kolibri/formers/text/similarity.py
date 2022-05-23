
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
from kolibri import ModelConfig, ModelTrainer, ModelLoader
import os, pickle
import numpy as np
import datetime

class TextSimilarityFormer():
    """
    Text classification pipeline

    """

    defaults={
        "default-cut-off": 0.95,
        "nb-returned": 5
    }
    def __init__(self,output_folder, X=None, y=None, model_name="similarity"):

        if X is not None:
            self.X=X
            config={}
            config["model"]="cosine"
            config["pipeline"]=["WordTokenizer", "TFIDFFeaturizer"]
            self._tfidf = ModelTrainer(ModelConfig(config))
            self._tfidf.fit(X, None)
            model_path=self._tfidf.persist(output_folder, fixed_model_name=model_name)

        self._tfidf=ModelLoader.load(os.path.join(output_folder,model_name))
        self.tfidf_matrix = self._tfidf.predict(X)
        if y is not None:
            self.classes={i:c for i, c in enumerate(y)}
            with open(os.path.join(output_folder, "classes.pickle"), 'wb') as fh:
                pickle.dump(self.classes, fh, pickle.HIGHEST_PROTOCOL)
        if y is None and os.path.exists(os.path.join(output_folder, "classes.pickle")):
            with open(os.path.join(output_folder, "classes.pickle"), 'fb') as fh:
                self.classes=pickle.load(fh)

    def __call__(self, data, y=None, cutoff=0.95, top_n=5):

        """
        Builds a model based on data.

        """
        tfidf_data=self._tfidf.predict(data)
        similarity= linear_kernel(tfidf_data, self.tfidf_matrix)


        similarity_indices = np.argsort(-similarity)[:,0:top_n]
        if y is None:
            similarity_resutls= [[(i,round(similarity[j][i], 2), self.classes[i]) for i in doc if similarity[j][i]> cutoff] for j, doc in enumerate(similarity_indices)]

        else:
            similarity_resutls = [[(i,round(similarity[j][i], 2), self.classes[i]) for i in doc if (similarity[j][i]> cutoff and self.classes[i] != y[j])] for j, doc in enumerate(similarity_indices)]

        return [results for results in similarity_resutls if results]

    def findMisclassification(self, df, classField):
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