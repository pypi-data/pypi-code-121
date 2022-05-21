from markdown import Markdown

MARKDOWN_EXTENSIONS = [
    "markdown_text_decorator"
]

md2html = Markdown(extensions=MARKDOWN_EXTENSIONS)

markdown_input = """

# Markdown Text Decoration

~~This is~~ strikethrough ~~line.~~

++This is++ insert ++line.++ 

--This is-- delete --line.--

^^This is^^ superscript ^^line^^

^This is^ subscript ^line^

!!This is!! mark !!line!!

{ Markdown Text Decorator : mɑ́ːkdàun tékst dékərèitər }

{ 日本語: !!Japanese!! } { 英語: !!English!! }

"""

html_output = md2html.convert(markdown_input)

print(html_output)

