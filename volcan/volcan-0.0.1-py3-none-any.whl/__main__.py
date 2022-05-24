from pathlib import Path
from sys import argv

from .frontend.lexer import Lexer


def main() -> None:
    command = argv[1]
    file = argv[2]

    if command == "lex":
        lexer = Lexer(file, Path(file).read_text())

        for token in lexer.tokenise():
            print(token)

    else:
        raise Exception("Unknown command")


if __name__ == "__main__":
    main()
