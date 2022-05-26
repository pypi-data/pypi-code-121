from rich.console import Console
from rich.highlighter import ReprHighlighter
from rich.panel import Panel

from servicefoundry.cli.const import MAX_WIDTH


class RichOutputCallBack:
    console = Console(width=MAX_WIDTH)
    highlighter = ReprHighlighter()

    def print_header(self, line):
        self.console.rule(f"{line}", style="cyan")

    def print_line(self, line):
        self.console.print(line)

    def print_lines_in_panel(self, lines, header):
        self.console.print(Panel(self.highlighter("\n".join(lines)), title=header))
