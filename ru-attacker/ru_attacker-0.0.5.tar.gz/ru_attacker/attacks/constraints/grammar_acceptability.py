from .basic_constraint import BasicConstraint
import language_tool_python

__all__ = ["GrammarAcceptability"]


class GrammarAcceptability(BasicConstraint):
    def __init__(self):
        self.tool = language_tool_python.LanguageTool('ru-RU')

    def check(self, original, transformed):
        matches = self.tool.check(transformed)
        grammar_mistakes = [1 for m in matches if m.category == "GRAMMAR"]
        if grammar_mistakes:
            return False
        else:
            return True
