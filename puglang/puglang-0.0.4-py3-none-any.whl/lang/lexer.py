class LexicalError(Exception):
    pass


class Lexer:
    def __init__(self):
        self.tokens = []
        self.source_code = ""

    def load(self, source_code):
        self.source_code = source_code

    def lex(self):
        if self.source_code == "":
            raise LexicalError("No source code for lexical scanning.")
        print("Lexing")
