"""
Markdown Text Decorator Extension
========================================

This is a [Python-Markdown](https://pypi.org/project/Markdown/) Text Decorator extension package.

Copyright 2022 Silver Bullet Software All rigths reserved.

License: MIT see) file:LICENSE

"""
from markdown.extensions import Extension
from markdown_text_decorator.processors import MarkdownTextDecoratorInlineProcessor

DECO_TARGET_TBL = {
    "strikethrough" : {
        "p": r'\~\~(.+?)\~\~',
        "t": "s",
    },
    "delete": {
        "p": r'--(.+?)--',
        "t": "del"
    },
    "insert": {
        "p": r'\+\+(.+?)\+\+',
        "t": "ins"
    },
    "sub": {
        "p": r'\^(.+?)\^',
        "t": "sub"
    },
    "super": {
        "p": r'\^\^(.+?)\^\^',
        "t": "sup"
    },
    "mark": {
        "p": r'!!(.+?)!!',
        "t": "mark"
    },
    "ruby" : {
        "p": r'{(.*?):(.*?)}',
        "t": "ruby>rt"
    }
}


PROC_BASE_PRIORITY=175


class MarkdownTextDecoratorExtension(Extension):


    def extendMarkdown(self, md):
        priority = PROC_BASE_PRIORITY
        for proc_name, props in DECO_TARGET_TBL.items():
            proc_item = MarkdownTextDecoratorInlineProcessor(pattern=props["p"], tags=props["t"])
            md.inlinePatterns.register(item=proc_item, name=proc_name, priority=priority)
            priority += 1


def makeExtension(**kwargs):
    return MarkdownTextDecoratorExtension(**kwargs)
