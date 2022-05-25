import sys


class OutputCallBack:
    def print_header(self, line):
        sys.stdout.write(f"{line}\n")

    def print_line(self, line):
        sys.stdout.write(f"{line}\n")

    def print_lines_in_panel(self, lines, header):
        self.print_header(header)
        for line in lines:
            self.print_line(line)

    def print_code_lines(self, lines, header, lang="python"):
        self.print_lines_in_panel(lines, header)
