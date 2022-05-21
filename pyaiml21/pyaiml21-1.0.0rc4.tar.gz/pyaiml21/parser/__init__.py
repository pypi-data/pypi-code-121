"""
AIML Parser.

This module represents the parser of AIML sources.

The parsing works in these phases:
    1) XML Parsing - an XML parser reads and returns the content of .aiml
       as if it was only .xml file
    2) transformation to ``ast.Node`` - returned XML AST is transformed
       to ast defined in the `ast` module (to generalize and enable simple
       exchange of XML parser by implementing only the `XMLParser` class
    3) extracting categories from the AST
    4) checking the AST for syntax errors and reporting them

To parse .aimlif files, similar approach is taken, with the difference,
that the file is parsed line by line and `XMLParser` receives only textual
representation of the AIML, not the file.
"""
from .parser import AIMLParser
from ._xml_lxml_parser import LXMLParser as XMLParser
from ._walker import TagSyntaxCheckerFn
from .logger import Logger


__all__ = [
    "AIMLParser",
    "XMLParser",
    "Logger",
    "TagSyntaxCheckerFn"
]
