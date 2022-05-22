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
        self.tag_list = tags.split(">")
        self.class_list = classes.split(">")
        self.style_list = styles.split(">")

    def handleMatch(self, m, data):
        top_el = None
        grp_idx = 1
        # TODO: Need to refactor.
        for tag in self.tag_list:
            tag = tag.strip()
            if top_el is None:
                top_el = etree.Element(tag)
                top_el.text = m.group(grp_idx).strip()
                if len(self.class_list) >= grp_idx and self.class_list[grp_idx - 1] != "":
                    top_el.set("class", self.class_list[grp_idx - 1])
                if len(self.style_list) >= grp_idx and self.style_list[grp_idx - 1] != "":
                    top_el.set("style", self.style_list[grp_idx - 1])
            else:
                sub_el = etree.SubElement(top_el, tag)
                sub_el.text = m.group(grp_idx).strip()
                if len(self.class_list) >= grp_idx and self.class_list[grp_idx - 1] != "":
                    sub_el.set("class", self.class_list[grp_idx - 1])
                if len(self.style_list) >= grp_idx and self.style_list[grp_idx - 1] != "":
                    sub_el.set("style", self.style_list[grp_idx - 1])
            grp_idx += 1
        return top_el, m.start(0), m.end(0)

