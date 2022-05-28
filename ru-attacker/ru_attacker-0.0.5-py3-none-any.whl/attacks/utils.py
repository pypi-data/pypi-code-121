import language_tool_python
import numpy as np
import tensorflow_hub as hub
import tensorflow_text

embed = hub.load("https://tfhub.dev/google/universal-sentence-encoder-multilingual/3")
tool = language_tool_python.LanguageTool('ru-RU')


def check_grammar(text):
    matches = tool.check(text)
    grammar_mistakes = [1 for m in matches if m.category == "GRAMMAR"]
    if grammar_mistakes:
        return False
    else:
        return True


def check_semantics(original, transformed):
    score = np.inner(embed(original), embed(transformed))
    if score >= 0.8:
        return True
    else:
        return False
