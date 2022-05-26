from IPython.display import display
from ipywidgets import Output, widgets
from pygments import highlight
from pygments.formatters import TerminalFormatter
from pygments.lexers import DiffLexer, PythonLexer

from servicefoundry.internal.io.output_callback import OutputCallBack


class NotebookOutputCallBack(OutputCallBack):
    def __init__(self):
        self.output: Output = None
        self.formatter = TerminalFormatter()

    def print_header(self, line):
        line = f"[{line}]"
        if self.output:
            with self.output:
                print(line)
        else:
            print(line)

    def print_line(self, line, lexer=None):
        if self.output:
            if lexer:
                line = highlight(line, lexer, self.formatter)
            with self.output:
                print(line)
        else:
            print(line)

    def print_lines_in_panel(self, lines, header=None):
        self.start_panel()
        self.print_header(header)
        for line in lines:
            self.print_line(line)
        self.close_panel()

    def print_code_in_panal(self, lines, header=None, lang="python"):
        if lang == "python":
            lexer = PythonLexer()
        elif lang == "diff":
            lexer = DiffLexer()
        else:
            lexer = self.lexer
        self.start_panel()
        if header:
            self.print_header(header)
        for line in lines:
            self.print_line(line, lexer=lexer)
        self.close_panel()

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
