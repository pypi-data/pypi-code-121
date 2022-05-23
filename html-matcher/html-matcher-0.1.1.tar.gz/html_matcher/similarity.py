class Similarity(object):

    def similarity(self, page1, page2):
        pass


class MixedSimilarity(Similarity):

    def __init__(self, similarity1, similarity2, k=0.5):
        self.similarity1 = similarity1
        self.similarity2 = similarity2
        self.k = k

    def similarity(self, document_1, document_2):
        return self.k * self.similarity1.similarity(document_1, document_2) + \
               (1 - self.k) * self.similarity2.similarity(document_1, document_2)
