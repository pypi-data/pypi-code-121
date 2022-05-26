from IPython.display import HTML, display
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer


def print_python_code(source_code):
    formatter = HtmlFormatter(noclasses=True)
    display(HTML((highlight(source_code, PythonLexer(), formatter))))
