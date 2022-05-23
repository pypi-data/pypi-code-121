from parsel import Selector

from html_matcher.similarity import Similarity


class StyleSimilarity(Similarity):

    def classes(self, html):
        doc = Selector(text=html)
        classes = set(doc.xpath('//*[@class]/@class').extract())
        result = set()
        for cls in classes:
            for _cls in cls.split():
                result.add(_cls)
        return result

    def jaccard_similarity(self, set1, set2):
        set1 = set(set1)
        set2 = set(set2)
        intersection = len(set1 & set2)

        if len(set1) == 0 and len(set2) == 0:
            return 1.0

        denominator = len(set1) + len(set2) - intersection
        return intersection / denominator

    def similarity(self, page1, page2):
        classes_page1 = self.classes(page1)
        classes_page2 = self.classes(page2)
        return self.jaccard_similarity(classes_page1, classes_page2)
