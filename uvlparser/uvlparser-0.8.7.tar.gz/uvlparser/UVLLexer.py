# Generated from uvlparser/UVL.g4 by ANTLR 4.7.2
from antlr4 import *
from io import StringIO
from typing.io import TextIO
import sys


from antlr_denter.DenterHelper import DenterHelper
from uvlparser.UVLParser import UVLParser


def serializedATN():
    with StringIO() as buf:
        buf.write("\3\u608b\ua72a\u8133\ub9ed\u417c\u3be7\u7786\u5964\2\35")
        buf.write("\u011d\b\1\4\2\t\2\4\3\t\3\4\4\t\4\4\5\t\5\4\6\t\6\4\7")
        buf.write("\t\7\4\b\t\b\4\t\t\t\4\n\t\n\4\13\t\13\4\f\t\f\4\r\t\r")
        buf.write("\4\16\t\16\4\17\t\17\4\20\t\20\4\21\t\21\4\22\t\22\4\23")
        buf.write("\t\23\4\24\t\24\4\25\t\25\4\26\t\26\4\27\t\27\4\30\t\30")
        buf.write("\4\31\t\31\4\32\t\32\4\33\t\33\4\34\t\34\4\35\t\35\3\2")
        buf.write("\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\2\3\3\3\3\3\3\3\3\3")
        buf.write("\3\3\3\3\3\3\3\3\3\3\4\3\4\3\5\3\5\3\5\3\6\3\6\3\7\3\7")
        buf.write("\3\b\3\b\3\t\3\t\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3\n\3")
        buf.write("\n\3\n\3\n\3\13\3\13\3\f\3\f\3\r\3\r\3\r\3\r\3\r\3\r\3")
        buf.write("\r\3\r\3\16\3\16\3\16\3\17\3\17\3\20\3\20\3\21\3\21\3")
        buf.write("\22\3\22\3\22\3\22\3\23\3\23\3\23\3\24\3\24\3\24\3\24")
        buf.write("\3\24\3\24\3\24\3\24\3\24\3\25\3\25\3\25\3\25\3\25\3\25")
        buf.write("\3\25\3\25\3\25\3\26\3\26\3\26\7\26\u0099\n\26\f\26\16")
        buf.write("\26\u009c\13\26\5\26\u009e\n\26\3\27\3\27\3\27\3\27\3")
        buf.write("\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27")
        buf.write("\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27")
        buf.write("\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\3\27\5\27\u00c3")
        buf.write("\n\27\3\27\3\27\5\27\u00c7\n\27\3\27\5\27\u00ca\n\27\3")
        buf.write("\30\3\30\7\30\u00ce\n\30\f\30\16\30\u00d1\13\30\3\31\3")
        buf.write("\31\3\31\3\31\3\31\3\31\3\31\3\31\3\31\5\31\u00dc\n\31")
        buf.write("\3\32\3\32\3\32\7\32\u00e1\n\32\f\32\16\32\u00e4\13\32")
        buf.write("\3\32\3\32\6\32\u00e8\n\32\r\32\16\32\u00e9\5\32\u00ec")
        buf.write("\n\32\5\32\u00ee\n\32\3\33\3\33\3\33\3\33\3\33\5\33\u00f5")
        buf.write("\n\33\3\33\5\33\u00f8\n\33\7\33\u00fa\n\33\f\33\16\33")
        buf.write("\u00fd\13\33\3\33\3\33\3\34\5\34\u0102\n\34\3\34\3\34")
        buf.write("\7\34\u0106\n\34\f\34\16\34\u0109\13\34\3\34\5\34\u010c")
        buf.write("\n\34\3\34\3\34\7\34\u0110\n\34\f\34\16\34\u0113\13\34")
        buf.write("\5\34\u0115\n\34\3\35\6\35\u0118\n\35\r\35\16\35\u0119")
        buf.write("\3\35\3\35\2\2\36\3\3\5\4\7\5\t\6\13\7\r\b\17\t\21\n\23")
        buf.write("\13\25\f\27\r\31\16\33\17\35\20\37\21!\22#\23%\24\'\25")
        buf.write(")\26+\2-\27/\30\61\31\63\32\65\33\67\349\35\3\2\7\3\2")
        buf.write("\63;\3\2\62;\4\2C\\c|\6\2\62;C\\aac|\3\2\"\"\2\u0134\2")
        buf.write("\3\3\2\2\2\2\5\3\2\2\2\2\7\3\2\2\2\2\t\3\2\2\2\2\13\3")
        buf.write("\2\2\2\2\r\3\2\2\2\2\17\3\2\2\2\2\21\3\2\2\2\2\23\3\2")
        buf.write("\2\2\2\25\3\2\2\2\2\27\3\2\2\2\2\31\3\2\2\2\2\33\3\2\2")
        buf.write("\2\2\35\3\2\2\2\2\37\3\2\2\2\2!\3\2\2\2\2#\3\2\2\2\2%")
        buf.write("\3\2\2\2\2\'\3\2\2\2\2)\3\2\2\2\2-\3\2\2\2\2/\3\2\2\2")
        buf.write("\2\61\3\2\2\2\2\63\3\2\2\2\2\65\3\2\2\2\2\67\3\2\2\2\2")
        buf.write("9\3\2\2\2\3;\3\2\2\2\5E\3\2\2\2\7N\3\2\2\2\tP\3\2\2\2")
        buf.write("\13S\3\2\2\2\rU\3\2\2\2\17W\3\2\2\2\21Y\3\2\2\2\23[\3")
        buf.write("\2\2\2\25g\3\2\2\2\27i\3\2\2\2\31k\3\2\2\2\33s\3\2\2\2")
        buf.write("\35v\3\2\2\2\37x\3\2\2\2!z\3\2\2\2#|\3\2\2\2%\u0080\3")
        buf.write("\2\2\2\'\u0083\3\2\2\2)\u008c\3\2\2\2+\u009d\3\2\2\2-")
        buf.write("\u00c9\3\2\2\2/\u00cb\3\2\2\2\61\u00db\3\2\2\2\63\u00ed")
        buf.write("\3\2\2\2\65\u00ef\3\2\2\2\67\u0114\3\2\2\29\u0117\3\2")
        buf.write("\2\2;<\7p\2\2<=\7c\2\2=>\7o\2\2>?\7g\2\2?@\7u\2\2@A\7")
        buf.write("r\2\2AB\7c\2\2BC\7e\2\2CD\7g\2\2D\4\3\2\2\2EF\7h\2\2F")
        buf.write("G\7g\2\2GH\7c\2\2HI\7v\2\2IJ\7w\2\2JK\7t\2\2KL\7g\2\2")
        buf.write("LM\7u\2\2M\6\3\2\2\2NO\7\60\2\2O\b\3\2\2\2PQ\7}\2\2QR")
        buf.write("\7\177\2\2R\n\3\2\2\2ST\7}\2\2T\f\3\2\2\2UV\7.\2\2V\16")
        buf.write("\3\2\2\2WX\7\177\2\2X\20\3\2\2\2YZ\7$\2\2Z\22\3\2\2\2")
        buf.write("[\\\7e\2\2\\]\7q\2\2]^\7p\2\2^_\7u\2\2_`\7v\2\2`a\7t\2")
        buf.write("\2ab\7c\2\2bc\7k\2\2cd\7p\2\2de\7v\2\2ef\7u\2\2f\24\3")
        buf.write("\2\2\2gh\7*\2\2h\26\3\2\2\2ij\7+\2\2j\30\3\2\2\2kl\7k")
        buf.write("\2\2lm\7o\2\2mn\7r\2\2no\7q\2\2op\7t\2\2pq\7v\2\2qr\7")
        buf.write("u\2\2r\32\3\2\2\2st\7c\2\2tu\7u\2\2u\34\3\2\2\2vw\7#\2")
        buf.write("\2w\36\3\2\2\2xy\7(\2\2y \3\2\2\2z{\7~\2\2{\"\3\2\2\2")
        buf.write("|}\7>\2\2}~\7?\2\2~\177\7@\2\2\177$\3\2\2\2\u0080\u0081")
        buf.write("\7?\2\2\u0081\u0082\7@\2\2\u0082&\3\2\2\2\u0083\u0084")
        buf.write("\7t\2\2\u0084\u0085\7g\2\2\u0085\u0086\7s\2\2\u0086\u0087")
        buf.write("\7w\2\2\u0087\u0088\7k\2\2\u0088\u0089\7t\2\2\u0089\u008a")
        buf.write("\7g\2\2\u008a\u008b\7u\2\2\u008b(\3\2\2\2\u008c\u008d")
        buf.write("\7g\2\2\u008d\u008e\7z\2\2\u008e\u008f\7e\2\2\u008f\u0090")
        buf.write("\7n\2\2\u0090\u0091\7w\2\2\u0091\u0092\7f\2\2\u0092\u0093")
        buf.write("\7g\2\2\u0093\u0094\7u\2\2\u0094*\3\2\2\2\u0095\u009e")
        buf.write("\7\62\2\2\u0096\u009a\t\2\2\2\u0097\u0099\t\3\2\2\u0098")
        buf.write("\u0097\3\2\2\2\u0099\u009c\3\2\2\2\u009a\u0098\3\2\2\2")
        buf.write("\u009a\u009b\3\2\2\2\u009b\u009e\3\2\2\2\u009c\u009a\3")
        buf.write("\2\2\2\u009d\u0095\3\2\2\2\u009d\u0096\3\2\2\2\u009e,")
        buf.write("\3\2\2\2\u009f\u00a0\7c\2\2\u00a0\u00a1\7n\2\2\u00a1\u00a2")
        buf.write("\7v\2\2\u00a2\u00a3\7g\2\2\u00a3\u00a4\7t\2\2\u00a4\u00a5")
        buf.write("\7p\2\2\u00a5\u00a6\7c\2\2\u00a6\u00a7\7v\2\2\u00a7\u00a8")
        buf.write("\7k\2\2\u00a8\u00a9\7x\2\2\u00a9\u00ca\7g\2\2\u00aa\u00ab")
        buf.write("\7q\2\2\u00ab\u00ca\7t\2\2\u00ac\u00ad\7q\2\2\u00ad\u00ae")
        buf.write("\7r\2\2\u00ae\u00af\7v\2\2\u00af\u00b0\7k\2\2\u00b0\u00b1")
        buf.write("\7q\2\2\u00b1\u00b2\7p\2\2\u00b2\u00b3\7c\2\2\u00b3\u00ca")
        buf.write("\7n\2\2\u00b4\u00b5\7o\2\2\u00b5\u00b6\7c\2\2\u00b6\u00b7")
        buf.write("\7p\2\2\u00b7\u00b8\7f\2\2\u00b8\u00b9\7c\2\2\u00b9\u00ba")
        buf.write("\7v\2\2\u00ba\u00bb\7q\2\2\u00bb\u00bc\7t\2\2\u00bc\u00ca")
        buf.write("\7{\2\2\u00bd\u00c2\7]\2\2\u00be\u00bf\5+\26\2\u00bf\u00c0")
        buf.write("\7\60\2\2\u00c0\u00c1\7\60\2\2\u00c1\u00c3\3\2\2\2\u00c2")
        buf.write("\u00be\3\2\2\2\u00c2\u00c3\3\2\2\2\u00c3\u00c6\3\2\2\2")
        buf.write("\u00c4\u00c7\5+\26\2\u00c5\u00c7\7,\2\2\u00c6\u00c4\3")
        buf.write("\2\2\2\u00c6\u00c5\3\2\2\2\u00c7\u00c8\3\2\2\2\u00c8\u00ca")
        buf.write("\7_\2\2\u00c9\u009f\3\2\2\2\u00c9\u00aa\3\2\2\2\u00c9")
        buf.write("\u00ac\3\2\2\2\u00c9\u00b4\3\2\2\2\u00c9\u00bd\3\2\2\2")
        buf.write("\u00ca.\3\2\2\2\u00cb\u00cf\t\4\2\2\u00cc\u00ce\t\5\2")
        buf.write("\2\u00cd\u00cc\3\2\2\2\u00ce\u00d1\3\2\2\2\u00cf\u00cd")
        buf.write("\3\2\2\2\u00cf\u00d0\3\2\2\2\u00d0\60\3\2\2\2\u00d1\u00cf")
        buf.write("\3\2\2\2\u00d2\u00d3\7v\2\2\u00d3\u00d4\7t\2\2\u00d4\u00d5")
        buf.write("\7w\2\2\u00d5\u00dc\7g\2\2\u00d6\u00d7\7h\2\2\u00d7\u00d8")
        buf.write("\7c\2\2\u00d8\u00d9\7n\2\2\u00d9\u00da\7u\2\2\u00da\u00dc")
        buf.write("\7g\2\2\u00db\u00d2\3\2\2\2\u00db\u00d6\3\2\2\2\u00dc")
        buf.write("\62\3\2\2\2\u00dd\u00ee\7\62\2\2\u00de\u00e2\t\2\2\2\u00df")
        buf.write("\u00e1\t\3\2\2\u00e0\u00df\3\2\2\2\u00e1\u00e4\3\2\2\2")
        buf.write("\u00e2\u00e0\3\2\2\2\u00e2\u00e3\3\2\2\2\u00e3\u00eb\3")
        buf.write("\2\2\2\u00e4\u00e2\3\2\2\2\u00e5\u00e7\7\60\2\2\u00e6")
        buf.write("\u00e8\t\3\2\2\u00e7\u00e6\3\2\2\2\u00e8\u00e9\3\2\2\2")
        buf.write("\u00e9\u00e7\3\2\2\2\u00e9\u00ea\3\2\2\2\u00ea\u00ec\3")
        buf.write("\2\2\2\u00eb\u00e5\3\2\2\2\u00eb\u00ec\3\2\2\2\u00ec\u00ee")
        buf.write("\3\2\2\2\u00ed\u00dd\3\2\2\2\u00ed\u00de\3\2\2\2\u00ee")
        buf.write("\64\3\2\2\2\u00ef\u00fb\7]\2\2\u00f0\u00f5\5\61\31\2\u00f1")
        buf.write("\u00f5\5\63\32\2\u00f2\u00f5\5/\30\2\u00f3\u00f5\5\65")
        buf.write("\33\2\u00f4\u00f0\3\2\2\2\u00f4\u00f1\3\2\2\2\u00f4\u00f2")
        buf.write("\3\2\2\2\u00f4\u00f3\3\2\2\2\u00f5\u00f7\3\2\2\2\u00f6")
        buf.write("\u00f8\7.\2\2\u00f7\u00f6\3\2\2\2\u00f7\u00f8\3\2\2\2")
        buf.write("\u00f8\u00fa\3\2\2\2\u00f9\u00f4\3\2\2\2\u00fa\u00fd\3")
        buf.write("\2\2\2\u00fb\u00f9\3\2\2\2\u00fb\u00fc\3\2\2\2\u00fc\u00fe")
        buf.write("\3\2\2\2\u00fd\u00fb\3\2\2\2\u00fe\u00ff\7_\2\2\u00ff")
        buf.write("\66\3\2\2\2\u0100\u0102\7\17\2\2\u0101\u0100\3\2\2\2\u0101")
        buf.write("\u0102\3\2\2\2\u0102\u0103\3\2\2\2\u0103\u0107\7\f\2\2")
        buf.write("\u0104\u0106\7\"\2\2\u0105\u0104\3\2\2\2\u0106\u0109\3")
        buf.write("\2\2\2\u0107\u0105\3\2\2\2\u0107\u0108\3\2\2\2\u0108\u0115")
        buf.write("\3\2\2\2\u0109\u0107\3\2\2\2\u010a\u010c\7\17\2\2\u010b")
        buf.write("\u010a\3\2\2\2\u010b\u010c\3\2\2\2\u010c\u010d\3\2\2\2")
        buf.write("\u010d\u0111\7\f\2\2\u010e\u0110\7\13\2\2\u010f\u010e")
        buf.write("\3\2\2\2\u0110\u0113\3\2\2\2\u0111\u010f\3\2\2\2\u0111")
        buf.write("\u0112\3\2\2\2\u0112\u0115\3\2\2\2\u0113\u0111\3\2\2\2")
        buf.write("\u0114\u0101\3\2\2\2\u0114\u010b\3\2\2\2\u01158\3\2\2")
        buf.write("\2\u0116\u0118\t\6\2\2\u0117\u0116\3\2\2\2\u0118\u0119")
        buf.write("\3\2\2\2\u0119\u0117\3\2\2\2\u0119\u011a\3\2\2\2\u011a")
        buf.write("\u011b\3\2\2\2\u011b\u011c\b\35\2\2\u011c:\3\2\2\2\27")
        buf.write("\2\u009a\u009d\u00c2\u00c6\u00c9\u00cf\u00db\u00e2\u00e9")
        buf.write("\u00eb\u00ed\u00f4\u00f7\u00fb\u0101\u0107\u010b\u0111")
        buf.write("\u0114\u0119\3\b\2\2")
        return buf.getvalue()


class UVLLexer(Lexer):

    atn = ATNDeserializer().deserialize(serializedATN())

    decisionsToDFA = [ DFA(ds, i) for i, ds in enumerate(atn.decisionToState) ]

    T__0 = 1
    T__1 = 2
    T__2 = 3
    T__3 = 4
    T__4 = 5
    T__5 = 6
    T__6 = 7
    T__7 = 8
    T__8 = 9
    T__9 = 10
    T__10 = 11
    T__11 = 12
    T__12 = 13
    NOT = 14
    AND = 15
    OR = 16
    EQUIVALENCE = 17
    IMPLICATION = 18
    REQUIRES = 19
    EXCLUDES = 20
    RELATION_WORD = 21
    WORD = 22
    BOOLEAN = 23
    NUMBER = 24
    VECTOR = 25
    NL = 26
    WS = 27

    channelNames = [ u"DEFAULT_TOKEN_CHANNEL", u"HIDDEN" ]

    modeNames = [ "DEFAULT_MODE" ]

    literalNames = [ "<INVALID>",
            "'namespace'", "'features'", "'.'", "'{}'", "'{'", "','", "'}'", 
            "'\"'", "'constraints'", "'('", "')'", "'imports'", "'as'", 
            "'!'", "'&'", "'|'", "'<=>'", "'=>'", "'requires'", "'excludes'" ]

    symbolicNames = [ "<INVALID>",
            "NOT", "AND", "OR", "EQUIVALENCE", "IMPLICATION", "REQUIRES", 
            "EXCLUDES", "RELATION_WORD", "WORD", "BOOLEAN", "NUMBER", "VECTOR", 
            "NL", "WS" ]

    ruleNames = [ "T__0", "T__1", "T__2", "T__3", "T__4", "T__5", "T__6", 
                  "T__7", "T__8", "T__9", "T__10", "T__11", "T__12", "NOT", 
                  "AND", "OR", "EQUIVALENCE", "IMPLICATION", "REQUIRES", 
                  "EXCLUDES", "INT", "RELATION_WORD", "WORD", "BOOLEAN", 
                  "NUMBER", "VECTOR", "NL", "WS" ]

    grammarFileName = "UVL.g4"

    def __init__(self, input=None, output:TextIO = sys.stdout):
        super().__init__(input, output)
        self.checkVersion("4.7.2")
        self._interp = LexerATNSimulator(self, self.atn, self.decisionsToDFA, PredictionContextCache())
        self._actions = None
        self._predicates = None


    class UVLDenter(DenterHelper):
        def __init__(self, lexer, nl_token, indent_token, dedent_token, ignore_eof):
            super().__init__(nl_token, indent_token, dedent_token, ignore_eof)
            self.lexer: UVLLexer = lexer

        def pull_token(self):
            return super(UVLLexer, self.lexer).nextToken()

    denter = None

    def nextToken(self):
        if not self.denter:
            self.denter = self.UVLDenter(self, self.NL, UVLParser.INDENT, UVLParser.DEDENT, True)
        return self.denter.next_token()



