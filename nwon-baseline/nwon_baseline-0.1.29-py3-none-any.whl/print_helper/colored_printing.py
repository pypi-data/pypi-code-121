from nwon_baseline.typings import TerminalColors, TerminalStyling


def print_green(text: str):
    print_color(text, TerminalColors.GREEN)


def print_blue(text: str):
    print_color(text, TerminalColors.BLUE)


def print_cyan(text: str):
    print_color(text, TerminalColors.CYAN)


def print_warning(text: str):
    print_color(text, TerminalColors.WARNING)


def print_error(text: str):
    print_color(text, TerminalColors.ERROR)


def print_color(text: str, color: "TerminalColors") -> None:
    print(f"{color.value}{text}{TerminalStyling.END_CHARACTER.value}")
