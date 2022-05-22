"""
Markdown Text Decorator Extension
========================================

This is a [Python-Markdown](https://pypi.org/project/Markdown/) Text Decorator extension package.

Copyright 2022 Silver Bullet Software All rigths reserved.

License: MIT see) file:LICENSE

"""
from markdown import Markdown

MARKDOWN_EXTENSIONS = [
    "markdown_text_decorator"
]

MARKDOWN_INPUT = """

# Markdown Text Decoration

~~This is~~ strikethrough ~~line~~

++This is++ insert ++line++ 

--This is-- delete --line--

^^This is^^ superscript ^^line^^

^This is^ subscript ^line^

!!This is!! mark !!line!!

=This is= underline =line=

==This is== underoverline ==line==

===This is=== overline ===line===

{ Markdown Text Decorator : mɑ́ːkdàun tékst dékərèitər }

{ 日本語: !!Japanese!! } { 英語: !!English!! }

"""


def run():
    md2html = Markdown(extensions=MARKDOWN_EXTENSIONS)
    html_output = md2html.convert(MARKDOWN_INPUT)
    return html_output

if __name__ == "__main__":
    html_output = run()
    print(html_output)
