"""Pretty-printing helpers"""
from colorama import Fore, Back, Style


def header(text):
    """Text styled like a header"""
    return f"\n{Back.LIGHTBLACK_EX} {text} {Style.RESET_ALL}"


def traffic_light(text, status="green"):
    """Green, amber or red text with leading symbol"""
    if status == "green":
        return f"{Fore.GREEN}[✔]{Style.DIM} {text} {Style.RESET_ALL}"
    if status == "amber":
        return f"{Fore.YELLOW}[-]{Style.DIM} {text} {Style.RESET_ALL}"
    if status == "red":
        return f"{Fore.RED}[✘]{Style.DIM} {text} {Style.RESET_ALL}"
    return "-"


def multiline_indent(multiline_string: str, levels: int = 2):
    """Indent each line by the specified number of spaces"""
    return " " * levels + ("\n" + " " * levels).join(multiline_string.splitlines())
