"""NanamiLang NException Data Type Class"""

# This file is a part of NanamiLang Project
# This project licensed under GNU GPL version 2
# Initially made by @jedi2light (aka Stoian Minaiev)

from typing import Tuple
from nanamilang import shortcuts
from ._exports import export
from .base import Base
from .type import Type


class NException(Base):
    """NanamiLang NException Type"""

    name: str = 'NException'
    _expected_type = Exception
    _python_reference: Exception
    _position: tuple
    _core_traceback: list
    purpose = 'Encapsulate Python 3 Exception'

    def __init__(self, reference: Tuple[Exception, Tuple]) -> None:
        """Initialize a new NException instance"""

        shortcuts.ASSERT_COLL_LENGTH_EQUALS_TO(
            reference,
            2,
            message='NException: reference should be a duplet'
        )
        # To avoid trapping into ValueError, let's assert length

        exception, self._position = reference
        # remember _what_ the error has been occurred and __where__

        self._position_message = ':'.join(map(str, self._position))
        # compile position message and store in self._position_message

        super().__init__(exception)
        # and then we can call Base.__init__() through Python3 super()

        self._core_traceback = []

        _t = exception.__traceback__
        while _t is not None:
            _f = _t.tb_frame.f_code.co_filename
            self._core_traceback.append(
                shortcuts.aligned('at', f'{_f}:{_t.tb_lineno}', 70)
            )
            _t = _t.tb_next
        # store self._core_traceback (it could be used in self.format)

    def to_py_str(self) -> str:
        """NanamiLang Exception, to_py_str() method"""

        return self._python_reference.__str__()

    def position(self) -> tuple:
        """NanamiLang NException, self._position getter"""

        return self._position

    @export()
    def instance(self) -> Type:
        """NanamiLang NException, instance method implementation"""

        return Type(Type.NException)

    def format(self, **kwargs) -> str:
        """NanamiLang NException, format() method implementation"""

        _max = 70
        _1space = ' '
        _2spaces = '  '

        _include_traceback = kwargs.get('include_traceback', False)
        if _include_traceback:
            _ = ['  ' + x for x in self._core_traceback]
            _with_traceback = '\n' + '\n'.join(_) + '\n'
        else:
            _with_traceback = shortcuts.aligned('', '<traceback hidden>', _max)

        _src = kwargs.get('src', '')
        if not _src:
            _with_e_highlight = '\n  '
        else:
            _with_e_highlight = f'\n{_2spaces}{_src}\n{_2spaces}{(self._position[2] - 1) * " "}^\n{_2spaces}'

        _msg = self._python_reference.__str__()
        _nam = self._python_reference.__class__.__name__

        _nm_separator = _1space if len(self._position_message) + len(_nam) + len(_msg) < _max else '\n' + _2spaces

        return f'\n  at {self._position_message}{_with_e_highlight}{_nam}:{_nm_separator}{_msg}\n{_with_traceback}'
