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

MARKDOWN_EXTENSION_CONFS={
    "markdown_text_decorator": { "priority": 90 }
}

MARKDOWN_INPUT = """

# Markdown Text Decoration Expression

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

# Python-Markdown Standard Expression 

This is nomal line

*This is* italic-1 *line*

_This is_ italic-2 _line_

**This is** bold-1 **line**

__This is__ bold-2 __line__

***This is*** bold+italic-1 ***line***

___This is___ bold+italic-2 ___line___

**_This is_** bold+italic-3 **_line_**

"""


def run():
    md2html = Markdown(extensions=MARKDOWN_EXTENSIONS,
                       extension_configs=MARKDOWN_EXTENSION_CONFS)
    html_output = md2html.convert(MARKDOWN_INPUT)
    return html_output

if __name__ == "__main__":
    html_output = run()
    print(html_output)
