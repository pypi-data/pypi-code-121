from antlr4 import CommonTokenStream, FileStream
from uvlparser.UVLLexer import UVLLexer
from uvlparser.UVLParser import UVLParser


def get_tree(argv):
    input_stream = FileStream(argv)
    lexer = UVLLexer(input_stream)
    stream = CommonTokenStream(lexer)
    parser = UVLParser(stream)
    tree = parser.feature_model()

    return tree
