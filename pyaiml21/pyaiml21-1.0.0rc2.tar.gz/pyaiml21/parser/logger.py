"""Logger to keep track of syntax errors."""
from pyaiml21.aiml import AIMLVersion
from pyaiml21.ast import Node
from typing import Set, Tuple, Optional

# within the logger, we represent the location as file, line and col, tag
_Location = Tuple[Optional[str], Optional[int], Optional[int], Optional[str]]
# reported message is a location and description
_ReportedMsg = Tuple[_Location, str]


def _extract_location(node: Node) -> _Location:
    """Extract location from the node."""
    return (node.filename, node.line, node.col, node.tag)


def _format_location(loc: _Location) -> str:
    """Return the formatted location used for reporting errors."""
    f, l, c, tag = loc
    file = f or "{unknown file/online}"
    lineno = "" if l is None else f"Line: {l}"
    colno = "" if c is None else f"Column: {c}"
    location = file
    if lineno:
        location += "\t" + lineno
    if colno:
        location += "\t" + colno
    if tag:
        return f"[{location}] <{tag}>:"
    return f"[{location}] TEXT:"


class Logger:
    """
    Logger instance is used to report error and warnings during parsing.

    The logger offers 3 levels of error messages:
        * weak warning - warnings that should be presented to the user
            only in the strict mode
        * warning - messages about elements that are either ignored or their
            correct representation can be deduced
        * errors - unrepairable errors in the representation

    Care should be taken that error-nous aiml constructs are not to be
    processed anymore as they contain in-interpretable code. Warnings are
    generally treated as if the corresponding element was not present or
    was modified accordingly.
    """

    def __init__(self):
        """Create an empty logger."""
        self._weak_warnings: Set[_ReportedMsg] = set()
        self._warnings: Set[_ReportedMsg] = set()
        self._errors: Set[_ReportedMsg] = set()

    def has_warnings(self) -> bool:
        """Return true if any warnings were found during parsing."""
        return len(self._warnings) > 0

    def has_errors(self) -> bool:
        """Return true if any errors were discovered during parsing."""
        return len(self._errors) > 0

    def weak_warning(self, node: Node, msg: str) -> None:
        """Report a weak warning."""
        loc = _extract_location(node)
        self._weak_warnings.add((loc, msg))

    def warning(self, node: Node, msg: str) -> None:
        """Report a warning about `node` as text `msg`."""
        loc = _extract_location(node)
        self._warnings.add((loc, msg))

    def error(self, node: Node, msg: str) -> None:
        """Report an error about `node` as text `msg`."""
        loc = _extract_location(node)
        self._errors.add((loc, msg))

    def report(self, with_stats: bool = False, strict: bool = False) -> str:
        """
        Generate a string report about all errors and warnings found.

        :param with_stats: True if summary of errors and warnings should
            be included
        :param strict: if true, include also weak warnings in the summary
        :return: string with formatted report
        """
        rep = []

        def format_noun(noun, count):
            return f"{count} {noun}{'s' if count != 1 else ''}"

        def process(list_: Set[_ReportedMsg], name):
            if list_:
                rep.append(f"{name}:")
                for loc, msg in sorted(list_):
                    loc_s = _format_location(loc)
                    rep.append(f"\t{loc_s}: {msg}")
                rep.append("")  # add a blank line

        process(self._errors, "Errors")
        warnings = set(self._warnings)
        if strict:
            warnings.update(self._weak_warnings)
        process(warnings, "Warnings")

        if with_stats:
            warns = format_noun("warning", len(warnings))
            errs = format_noun("error", len(self._errors))
            rep.append(f"Summary: {errs}, {warns}")
        return "\n".join(rep)

    #
    # specialized methods
    #

    def warn_unexpected_attr(self, node: Node, attr: str):
        """Issue a warning about unexpected attribute."""
        self.warning(node, f"Unexpected attribute: \"{attr}\"")

    def error_missing_attr(self, node: Node, attr: str):
        """Issue an error about missing required attribute."""
        self.error(node, f"Missing attribute: \"{attr}\"")

    def error_xml_syntax(self, msg: str, file: Optional[str],
                         line: Optional[int] = None,
                         col: Optional[int] = None):
        """Issue an error when XML is malformed."""
        dummy_node = Node.Value("", filename=file, line=line, col=col)
        self.error(dummy_node, f"XML parsing error: \"{msg}\"")

    def warn_xml_syntax(self, msg: str, file: Optional[str],
                        line: Optional[int] = None,
                        col: Optional[int] = None):
        """Issue a warning during XML parsing."""
        dummy_node = Node.Value("", filename=file, line=line, col=col)
        self.warning(dummy_node, f"XML parsing warning: \"{msg}\"")

    def warn_unexpected_element(self, node: Node):
        """Issue a warning about unexpected element."""
        # we allow for spaces to separate any elements
        if node.text == " ":
            return
        elem = node.tag or f"\"{node.text}\""
        self.warning(node, f"Unexpected element: {elem}")

    def error_duplicate_element(self, node: Node):
        """Issue an error about duplicated element."""
        self.error(node, f"Found duplicate element: {node.tag}")

    def error_unexpected_element(self, node: Node):
        """Issue an error about unexpected element."""
        # we allow for spaces to separate any elements
        if node.text == " ":
            return
        self.error(node, f"Unexpected element: {node.tag or f'{node.text}'}")

    def warn_not_defined(self, node: Node, def_version: AIMLVersion):
        """Warn if `node.tag` is not defined in given version."""
        self.warning(node, f"not defined in {node.aiml_version}, "
                           f"first defined in {def_version.value} "
                           f"- using forward compatible mode")

    def warn_deprecated(self, node: Node, last_version: AIMLVersion):
        """Issue a deprecation warning about `node`."""
        self.warning(node, f"deprecated in {node.aiml_version}, "
                           f"last defined in {last_version.value}")
