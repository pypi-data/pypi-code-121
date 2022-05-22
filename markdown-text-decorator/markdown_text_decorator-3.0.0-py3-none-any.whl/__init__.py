"""
Markdown Text Decorator Extension
========================================

This is a [Python-Markdown](https://pypi.org/project/Markdown/) Text Decorator extension package.

Copyright 2022 Silver Bullet Software All rigths reserved.

License: MIT see) file:LICENSE

"""
from markdown.extensions import Extension
from markdown_text_decorator.processors import MarkdownTextDecoratorInlineProcessor

TARGET_TYPE_TBL = {
    "strikethrough" : {
        "p": r'\~\~(.+?)\~\~',
        "t": "s",
        "c": "",
        "s": ""
    },
    "delete": {
        "p": r'--(.+?)--',
        "t": "del",
        "c": "",
        "s": ""
    },
    "insert": {
        "p": r'\+\+(.+?)\+\+',
        "t": "ins",
        "c": "",
        "s": ""
    },
    "sub": {
        "p": r'\^(.+?)\^',
        "t": "sub",
        "c": "",
        "s": ""
    },
    "super": {
        "p": r'\^\^(.+?)\^\^',
        "t": "sup",
        "c": "",
        "s": ""
    },
    "mark": {
        "p": r'!!(.+?)!!',
        "t": "mark",
        "c": "",
        "s": ""
    },
    "ruby" : {
        "p": r'{(.*?):(.*?)}',
        "t": "ruby>rt",
        "c": "",
        "s": ""
    },
    "underline" : {
        "p": r'=(.*?)=',
        "t": "span",
        "c": "underline",
        "s": "text-decoration: underline"
    },
    "underoverline" : {
        "p": r'==(.*?)==',
        "t": "span",
        "c": "underoverline",
        "s": "text-decoration: underline overline"
    },
    "overline" : {
        "p": r'===(.*?)===',
        "t": "span",
        "c": "overline",
        "s": "text-decoration: overline"
    }
}


PROC_BASE_PRIORITY=175


class MarkdownTextDecoratorExtension(Extension):


    def extendMarkdown(self, md):
        priority = PROC_BASE_PRIORITY
        for proc_name, props in TARGET_TYPE_TBL.items():
            proc_item = MarkdownTextDecoratorInlineProcessor(
                pattern=props["p"], tags=props["t"], classes=props["c"], styles=props["s"]
            )
            md.inlinePatterns.register(item=proc_item, name=proc_name, priority=priority)
            priority += 1


def makeExtension(**kwargs):
    return MarkdownTextDecoratorExtension(**kwargs)
