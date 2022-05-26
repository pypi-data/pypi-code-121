import sys


class OutputCallBack:
    def print_header(self, line):
        sys.stdout.write(f"{line}\n")

    def print_line(self, line):
        sys.stdout.write(f"{line}\n")

    def print_lines_in_panel(self, lines, header=None):
        self.print_header(header)
        for line in lines:
            self.print_line(line)

    def print_code_in_panal(self, lines, header=None, lang="python"):
        self.print_lines_in_panel(lines, header)
