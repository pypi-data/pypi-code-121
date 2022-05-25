import os

from IPython.display import HTML, display
from ipywidgets import Output, widgets
from pygments import highlight
from pygments.formatters import HtmlFormatter
from pygments.lexers import PythonLexer
from pygments.lexers.diff import DiffLexer

from servicefoundry.internal.output_callback import OutputCallBack


class NotebookOutputCallBack(OutputCallBack):
    def __init__(self):
        self.output: Output = None

    def print_header(self, line):
        line = f"[{line}]\n"
        if self.output:
            self.output.append_stdout(line)
        else:
            print(line)

    def print_line(self, line):
        line = f"{line}\n"
        if self.output:
            self.output.append_stdout(line)
        else:
            print(line)

    def print_lines_in_panel(self, lines, header):
        self.start_panel()
        self.print_header(header)
        for line in lines:
            self.print_line(line)
        self.close_panel()

    def print_code_lines(self, lines, header, lang="python"):
        formatter = HtmlFormatter(noclasses=True)
        if lang == "python":
            lexer = PythonLexer()
        elif lang == "diff":
            lexer = DiffLexer()
        else:
            raise TypeError(f"Unexpected code lang {lang}")
        display(HTML((highlight(os.linesep.join(lines), lexer, formatter))))

    def start_panel(self):
        output = Output(
            layout=widgets.Layout(width="100%", height="auto", border="1px solid black")
        )
        box = widgets.Box(
            children=[output], layout=widgets.Layout(width="100%", height="auto")
        )
        display(box)
        self.output = output

    def close_panel(self):
        self.output = None
