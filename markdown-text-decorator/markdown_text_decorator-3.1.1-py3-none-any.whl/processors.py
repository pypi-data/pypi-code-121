"""
Markdown Text Decorator Extension
========================================

This is a [Python-Markdown](https://pypi.org/project/Markdown/) Text Decorator extension package.

Copyright 2022 Silver Bullet Software All rigths reserved.

License: MIT see) file:LICENSE

"""
import xml.etree.ElementTree as etree
from markdown.inlinepatterns import InlineProcessor


class MarkdownTextDecoratorInlineProcessor(InlineProcessor):

    def __init__(self, pattern, tags, classes, styles):
        super().__init__(pattern)
        params = { "t": tags.split(">"), "c": classes.split(">"), "s": styles.split(">"), "r": None, "i": 0 }
        self.data = {}
        for key, value in params.items():
            self.data[key] = value
        
    def set_elm_attrs(self, elm, text):
        elm.text = text.strip()
        attrs = {"class": self.data["c"], "style": self.data["s"] }
        for attr, value in attrs.items():
            if len(value) >= self.data["i"] + 1 and value[self.data["i"]] != "":
                elm.set(attr, value[self.data["i"]])

    def run(self, matched, tag):
        if self.data["r"] is None:
            self.data["r"] = etree.Element(tag)
            self.set_elm_attrs(self.data["r"], matched.group(self.data["i"] + 1))
            return
        child = etree.SubElement(self.data["r"], tag)
        self.set_elm_attrs(child, matched.group(self.data["i"] + 1))


    def handleMatch(self, m, data):
        self.data["r"] = None
        self.data["i"] = 0
        for tag in self.data["t"]:
            self.run(m, tag.strip())
            self.data["i"] += 1
        return self.data["r"], m.start(0), m.end(0)

