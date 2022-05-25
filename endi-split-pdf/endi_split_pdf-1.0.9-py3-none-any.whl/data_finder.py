"""
Module grouping data finder

A data finder takes a string representation of a pdf page and some
configuration values and returns the data we're looking for


In [16]: from endi_split_pdf.utils import get_page_text

In [17]: from endi_split_pdf import data_finder

In [18]: pdf_str = get_page_text('./salaire_2020_11.pdf', '1')

In [19]: finder = data_finder.RegexDataFinder(rb'\s[5,9][\w]{3,6}\s')

In [20]: res = finder.find(pdf_str)

In [21]: res.group(0)
Out[21]: b' 9AAAEZ0\n'




>>> finder = RegexDataFinder(regex=rb"[a-b]6")
>>> print(finder.find(pdf_string))

>>> finder = CoordinateDataFinder(line=5, alternate_line=6, start_column=10,
end_column=20)
>>> print(finder.find(pdf_string))
"""
import re
from .errors import AutosplitError
from .log_config import mk_logger


def ensure_str(data_str):
    """
    Ensure the given data_str is effectively a str
    """
    result = data_str
    if isinstance(result, bytes):
        result = result.decode('utf-8')
    return result


def clean_blank_chars(data_str):
    """
    Clean blank characters in data_str
    """
    _cleaner = re.compile(r'(^\s+|\s+$)')
    return _cleaner.sub('', data_str)


class BaseDataFinder():
    def __init__(
        self,
        column=None,
        end_column=None,
        **kwargs,
    ):
        self.logger = mk_logger('endi_split_pdf.data_finder')
        self.column = column
        self.end_column = end_column


class RegexDataFinder(BaseDataFinder):

    def __init__(
        self,
        regex=None,
        strict=False,
        from_line=None,
        to_line=None,
        regex_group_name=0,
        column=None,
        end_column=None,
        **kwargs,
    ):
        super(RegexDataFinder, self).__init__(column, end_column)
        regex = ensure_str(regex)
        try:
            self.regex = re.compile(regex)
        except Exception as err:
            print(regex)
            raise AutosplitError(
                "Invalid regex '{}' ({})".format(regex, err)
            )
        self.strict = strict

        if from_line:
            self.from_line = max(int(from_line) - 1, 0)
        else:
            self.from_line = None

        if to_line:
            self.to_line = max(int(to_line) - 1, 0)
        else:
            self.to_line = None

        if self.from_line and self.to_line and self.from_line > self.to_line:
            raise Exception(
                "from_line ({}) should not be greater than to_line "
                "({})".format(self.from_line, self.to_line)
            )

        self.regex_group_name = regex_group_name

    def _restrict_data(self, data_str):
        """
        Restrict the data to treat regarding from_line and to_line
        """
        lines = data_str.splitlines()
        if self.to_line is not None:
            lines = lines[:self.to_line]

        if self.from_line is not None:
            lines = lines[self.from_line:]

        if self.end_column is not None:
            lines = [line[:self.end_column] for line in lines]

        if self.column is not None:
            lines = [line[self.column:] for line in lines]

        return '\n'.join(lines)

    def _debug(self, data_str, match_num):
        self.logger.debug(self.regex)
        self.logger.debug(data_str)
        self.logger.debug("{} matched".format(match_num))

    def find(self, data_str):
        """
        Find matches in the data_str object
        :param str data_str: The data str to check

        :returns: the matching entry
        :rtype: str or None
        """
        data_str = ensure_str(data_str)
        result = None

        if self.from_line is not None or self.to_line is not None:
            data_str = self._restrict_data(data_str)

        match_num = len(self.regex.findall(data_str))

        if self.strict and match_num > 1:
            self.logger.debug("+ Strict mode and more than one match")
            self._debug(data_str, match_num)
        elif match_num == 0:
            self.logger.debug("+ No match at all")
            self._debug(data_str, match_num)
        else:
            result = self.regex.search(data_str).group(self.regex_group_name)
            result = clean_blank_chars(result)
        return result


class CoordinateDataFinder(BaseDataFinder):

    def __init__(
            self, line, column=None, end_column=None, prefix=None, **kwargs
    ):
        super(CoordinateDataFinder, self).__init__(column, end_column)
        self.line = int(line)
        if column is not None:
            column = int(column)
        self.column = column
        self.end_column = end_column
        self.prefix = ensure_str(prefix)

    def find(self, data_str):
        """
        Find matches in the data_str object
        :param str data_str: The data str to check

        :returns: the matching entry
        :rtype: str or None
        """
        data_str = ensure_str(data_str)
        result = None
        line = data_str.splitlines()[self.line - 1]

        if self.end_column:
            line = line[:self.end_column].strip()

        if self.column:
            line = line[self.column:].strip()

        if self.prefix is not None:
            if self.prefix in line:
                result = clean_blank_chars(
                    line.split(self.prefix)[1]
                )
        else:
            result = clean_blank_chars(line)

        self.logger.debug(self.__class__)
        self.logger.debug(result)

        return result


class FrNameRegexDataFinder(RegexDataFinder):
    """
    Custom regex class to find names in fr format (expect to find it in address
    block (not start of the line and last words in line)
    """
    def __init__(self, **kw):
        kw['regex'] = (
            r"(?i)[ ]+(M.|M|Mme|Mlle|Madame|Monsieur|Mademoiselle)[ ]+(?P<name>"
            r"[-\w ']+)(\n|$)")
        kw['regex_group_name'] = 'name'
        RegexDataFinder.__init__(self, **kw)


class FrNameNoMmeRegexDataFinder(RegexDataFinder):
    """
    Custom regex class to find names in fr format (expect to find it in address
    block (not start of the line and last words in line)
    """
    def __init__(self, **kw):
        kw['regex'] = r"[ ]+(?P<name>[-\w ']+)(\n|$)"
        kw['regex_group_name'] = 'name'
        RegexDataFinder.__init__(self, **kw)


FINDERS = {
    'coordinates': CoordinateDataFinder,
    'regex': RegexDataFinder,
    'frname_regex': FrNameRegexDataFinder,
    'frname_no_mme_regex': FrNameNoMmeRegexDataFinder,
}
