from io import StringIO

import lxml
from apted.apted import APTED
from apted.config import Config

from similarity import Similarity
from utils import json_count_elements, html_to_json, html_to_json_improved


class CustomConfig(Config):
    def rename(self, node1, node2):
        """Compares attribute .value of trees"""
        return 1 if node1["tag"] != node2["tag"] else 0

    def children(self, node):
        """Get left and right children of binary tree"""
        return [x for x in node["children"] if x]


class AllPathTreeEditDistance(Similarity):

    def similarity(self, page1, page2):
        html1 = lxml.html.parse(StringIO(page1)).find('body')
        tree1 = html_to_json(html1)
        html2 = lxml.html.parse(StringIO(page2)).find('body')
        tree2 = html_to_json(html2)
        apted = APTED(tree1, tree2, CustomConfig())
        matching = apted.compute_edit_distance()
        count = json_count_elements(tree1, "tag", "children")
        count += json_count_elements(tree2, "tag", "children")
        return 1 - (matching / count)


class AllPathTreeEditDistanceOptimized(AllPathTreeEditDistance):

    def similarity(self, page1, page2):
        html1 = lxml.html.parse(StringIO(page1)).find('body')
        tree1 = html_to_json_improved(html1)
        html2 = lxml.html.parse(StringIO(page2)).find('body')
        tree2 = html_to_json_improved(html2)
        apted = APTED(tree1, tree2, CustomConfig())
        matching = apted.compute_edit_distance()
        count = json_count_elements(tree1, "tag", "children")
        count += json_count_elements(tree2, "tag", "children")
        return 1 - (matching / count)
