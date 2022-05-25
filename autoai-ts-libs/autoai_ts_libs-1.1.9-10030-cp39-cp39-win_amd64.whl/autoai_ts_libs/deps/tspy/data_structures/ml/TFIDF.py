class TFIDF:

    def __init__(self, tsc, j_tfidf):
        self._tsc = tsc
        self._j_tfidf = j_tfidf

    def predict(self, term_map, default_doc=None):

        j_term_map = self._tsc.java_bridge.convert_to_java_map(term_map)
        if default_doc is None:
            return self._j_tfidf.predict(j_term_map)
        else:
            return self._j_tfidf.predict(j_term_map, default_doc)

    def get_weight(self, doc, term):
        return self._j_tfidf.getWeight(doc, term)

    def get_term_freq(self, doc, term):
        return self._j_tfidf.getTermFreq(doc, term)

    def get_doc_freq(self, term):
        return self._j_tfidf.getDocFreq(term)

    def __str__(self):
        return str(self._j_tfidf.toString())

    def __repr__(self):
        return self.__str__()
