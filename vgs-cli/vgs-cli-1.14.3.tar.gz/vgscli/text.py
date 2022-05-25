from termcolor import colored


def bold(text: str) -> str:
    return colored(text, attrs=['bold'])


def green(text: str) -> str:
    return colored(text, color='green')
