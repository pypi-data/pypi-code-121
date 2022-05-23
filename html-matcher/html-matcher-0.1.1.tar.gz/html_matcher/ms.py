import difflib
from io import StringIO

import lxml.html

from html_matcher.similarity import Similarity
from html_matcher.utils import html_to_json_improved, json_to_array


class MatchingSubsequences(Similarity):

    def get_tags(self, doc):
        tags = list()

        for el in doc.getroot().iter():
            if isinstance(el, lxml.html.HtmlElement):
                tags.append(el.tag)

        return tags

    def similarity(self, page1, page2):
        document_1 = lxml.html.parse(StringIO(page1))
        document_2 = lxml.html.parse(StringIO(page2))
        tags1 = self.get_tags(document_1)
        tags2 = self.get_tags(document_2)
        diff = difflib.SequenceMatcher(a=tags1, b=tags2)
        return diff.ratio()


class MatchingSubsequencesOptimized(MatchingSubsequences):

    def get_tags(self, doc):
        json = html_to_json_improved(doc.find('body'))
        return json_to_array(json, "tag", "children")
