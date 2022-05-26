"""Log term styles."""

from pygments import highlight  # noqa
from pygments.formatters.terminal256 import Terminal256Formatter # noqa
from pygments.lexers.web import JsonLexer  # noqa
from pygments.style import Style
from pygments.token import Keyword, Name, String, Number, Token


class BaseStyle(Style):
    """Base log style."""

    default_style = ""


class StyleDefault(BaseStyle):
    """Log style default or notset."""

    styles = {
        Token:  'bold #808080',
        Keyword: 'bold #808080',
        String: '#c0c0c0',
        Number: '#c0c0c0',
    }


class StyleDebug(BaseStyle):
    """Log style debug."""

    styles = {
        Token: '#5f5faf',
        Name: 'bold #5f5faf',
        String: '#8787ff',
        Number: '#8787ff',
    }


class StyleInfo(BaseStyle):
    """Log style info."""

    styles = {
        Token: '#afd700',
        Name: 'bold #afd700',
        String: '#afaf00',
        Number: '#afaf00',
    }


class StyleWarning(BaseStyle):
    """Log style warning."""

    styles = {
        Token: '#ffaf00',
        Name: 'bold #ffaf00',
        String: '#af8700',
        Number: '#af8700',
    }


class StyleError(BaseStyle):
    """Log style error."""

    styles = {
        Token: '#FF0000',
        Name: 'bold #FF0000',
        String: '#E9967A',
        Number: '#E9967A',
    }
