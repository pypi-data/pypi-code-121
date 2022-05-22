from abc import ABC
from abc import abstractmethod
from collections.abc import Mapping, Sequence, MutableSequence, MutableMapping
from enum import Enum
from logging import Logger
from logging import getLogger
from typing import Optional, Union, Iterator, Any, Protocol


class HtmlObject(ABC):
    """Abstract parent object for all HTML elements"""
    #: The string used within the html tags. E.g. "br" or "div" ...
    TAG: str

    ALIGNMENT_MAP = {'r': 'right',
                     'right': 'right',
                     'l': 'left',
                     'left': 'left',
                     'c': 'center',
                     'center': 'center'}

    root_app: Optional['PySpassApp'] = None
    parent: Optional['HtmlObject'] = None

    #: All elements included in the html tag in form of a dict
    tag_content: dict
    #: All css styles included in the html tag in form of a dict
    css_styles: dict
    #: Html id to be inserted in tag
    _id_html: Optional[str]
    #: Html class to be inserted in tag
    _class_html: Optional[str]
    #: Depth of indentation for nicely formatted html
    indents: int = 0

    def __init__(self, id_html: str = None, class_html: str = None):
        self.tag_content: dict = {}
        self.css_styles: dict = {}
        self.id_html = id_html
        self.class_html = class_html
        self.indents: int = 0

    @property
    def id_html(self):
        return self._id_html

    @id_html.setter
    def id_html(self, value):
        self._id_html = value
        if value:
            self.tag_content['id'] = value

    @property
    def class_html(self):
        return self._class_html

    @class_html.setter
    def class_html(self, value):
        self._class_html = value
        if value:
            self.tag_content['class'] = value

    def get_form(self) -> Optional['HtmlForm']:
        """Recursive search for parent form, if exsiting

        Raise error if nested form is detected.
        """
        if not self.parent:
            parent_form = None
        else:
            if isinstance(self.parent, HtmlForm):
                parent_form = self.parent
            else:
                parent_form = self.parent.get_form()
            if parent_form and (parent_form.get_form() or
                                isinstance(self, HtmlForm)):
                super_parent_form: Optional[HtmlForm] = parent_form.get_form()
                debug_str = super_parent_form.id_html if super_parent_form else self.id_html
                raise Exception(f"Nested forms detected! {parent_form.id_html} within {debug_str}.")
        return parent_form


class HtmlContainer(HtmlObject, list, ABC):
    """Abstract Html object for all Html objects that are container for further elements. E.g. div, p, form ..."""

    def add(self, content: Union[HtmlObject, str, int, float]) -> HtmlObject:
        """Add and register an element to the container

        Adding an element will set this object as the parent object and increase the indent counter.
        If the element is a valid HtmlObject, this new child will be returned for further processing.
        If the element is a string, then this parent object will be returned instead.

        :param content: The content to be inserted into the container.
        """
        self.append(content)
        if isinstance(content, HtmlObject):
            content.parent = self
            content.indents += 1
            return content
        else:
            return self

    def br(self, count: int = 1):
        for i in range(count):
            self.append('<br />\n')
        return self

    def hr(self):
        self.append('<hr />\n')
        return self

    def div(self, content=None, id_html: str = None, class_html: str = None):
        div = HtmlDiv(content, id_html=id_html, class_html=class_html)
        self.add(div)
        return div

    def p(self, content=None, id_html: str = None, class_html: str = None):
        p = HtmlP(content, id_html=id_html, class_html=class_html)
        self.add(p)
        return p

    def span(self, content=None, id_html: str = None, class_html: str = None):
        span = HtmlSpan(content, id_html=id_html, class_html=class_html)
        self.add(span)
        return span

    def form(self, id_html: str = None):
        form = HtmlForm(id_html)
        self.add(form)
        return form

    def table(self) -> 'HtmlTable':
        table = HtmlTable()
        self.add(table)
        return table

    def h1(self, content=None, id_html: Optional[str] = None, class_html: Optional[str] = None):
        h1 = HtmlH1(content, id_html, class_html)
        self.add(h1)
        return h1

    def h2(self, content=None, id_html: Optional[str] = None, class_html: Optional[str] = None):
        h2 = HtmlH2(content, id_html, class_html)
        self.add(h2)
        return h2

    def h3(self, content=None, id_html: Optional[str] = None, class_html: Optional[str] = None):
        h3 = HtmlH3(content, id_html, class_html)
        self.add(h3)
        return h3

    def link(self, content=None, href: str = None, target: str = "_blank"):
        link = HtmlLink(**{key: value for key, value in locals().items() if key not in 'self'})
        self.add(link)
        return link

    def label(self, content: str = None, for_id: str = None) -> 'HtmlLabel':
        label = HtmlLabel(content=content, for_id=for_id)
        self.add(label)
        return label

    def hidden(self, name, value=None, id_html: str = None) -> 'HtmlHidden':
        hidden = HtmlHidden(name=name, value=value, id_html=id_html)
        self.add(hidden)
        return hidden

    def submit(self, name: Union[str, Enum], value=None, id_html: str = None, class_html: str = None) -> 'HtmlSubmit':
        sub = HtmlSubmit(name=name, value=value, id_html=id_html, class_html=class_html)
        self.add(sub)
        return sub

    def button(self, name: str, value=None, id_html: str = None, class_html: str = None):
        sub = HtmlButton(name=name, value=value, id_html=id_html, class_html=class_html)
        self.add(sub)
        return sub

    def checkbox(self, name, value=1, label=None, var_input: Union[int, str] = None, autosubmit: bool = False,
                 id_html: str = None, class_html: str = None, label_trailing: bool = True):
        """

        :param label_trailing: If true, the label will be added after the checkbos. If false, the label comes first.
        :return:
        """
        chkbx = HtmlCheckbox(name=name, value=value, var_input=var_input, autosubmit=autosubmit,
                             id_html=id_html, class_html=class_html)
        label = HtmlLabel(content=label, for_id=id_html)
        if not label_trailing:
            self.add(label)
        self.add(chkbx)
        if label_trailing:
            self.add(label)
        return chkbx

    def script(self, content: str = None, src: str = None, script_type: str = None) -> 'HtmlScript':
        """Register a script file for the header

        :param content: TODO
        :param src: path to the file for the src tag
        :param script_type: TODO
        :return: HtmlScript
        """
        script = HtmlScript(content=content, src=src, script_type=script_type)
        self.add(script)
        return script

    def dropdown(self, name: str, codes_source: Union[Sequence, Mapping], var_input: Optional[str] = None,
                 autosubmit: bool = False, missing_allowed: bool = True, multiple: bool = False, size: int = 1,
                 optgroups: Optional[Mapping] = None):
        return self.add(HtmlSelect(**{key: value for key, value in locals().items() if key not in 'self'}))

    def textinput(self, name: str, var_input: Optional[str] = None, size: int = 20, alignment: Optional[str] = None,
                  class_html: str = None):
        return self.add(HtmlTextInput(**{key: value for key, value in locals().items() if key not in 'self'}))

    def password(self, name: str, var_input: Optional[str] = None, size: int = 20):
        return self.add(HtmlPassword(**{key: value for key, value in locals().items() if key not in 'self'}))

    def textarea(self, name: str, var_input: Optional[str] = None, rows: int = 4, cols: int = 50):
        return self.add(HtmlTextArea(**{key: value for key, value in locals().items() if key not in 'self'}))

    def result_listing(self, content: Sequence, mapping=None, show_all: bool = False, rowcount_max: int = 200,
                       alignments: Optional[str] = None) -> Union['ResultListing', HtmlObject]:
        return self.add(ResultListing(content, mapping, show_all, rowcount_max, alignments))

    def result_choice(self, content: Sequence, listing_index: Union[str, Sequence], row_selected=None,
                      mapping: Mapping[str, str] = None, show_all: bool = False, alignments: Optional[str] = None,
                      rowcount_max: int = 200) -> Union['ResultChoice', HtmlObject]:
        """Factory function for creation of ResultChoice"""
        return self.add(ResultChoice(content, listing_index, row_selected, mapping, show_all, rowcount_max, alignments))

    def result_editor(self, content: Sequence, listing_index: Union[str, Sequence[str]],
                      row_selected: Union[str, Mapping, Sequence[Mapping]],
                      mapping: Optional[Mapping[str, str]] = None,
                      show_all: bool = False, rowcount_max: int = 200, columns_protected: list = None,
                      alignments: Optional[str] = None) -> Union['ResultEditor', HtmlObject]:
        return self.add(ResultEditor(content, listing_index, row_selected, mapping, show_all, rowcount_max,
                                     columns_protected, alignments))

    def __str__(self):
        if self.css_styles:
            css_styles_str = ';'.join([key + ':' + value for key, value in self.css_styles.items()])
            self.tag_content['style'] = css_styles_str
        tag_content_str = ' '.join([f'{key}="{value}"' for key, value in self.tag_content.items()])
        return f"<{self.TAG}{' ' + tag_content_str if tag_content_str else ''}>" \
               f"\n{''.join([str(child) for child in self])}\n</{self.TAG}>\n"


class HtmlCell(HtmlContainer):
    TAG: str = 'td'

    def __init__(self, content=None):
        super().__init__()
        if content:
            self.append(content)


class HtmlHeadCell(HtmlCell):
    TAG: str = 'th'


class HtmlRow(HtmlContainer):
    """Object for standard HTML row"""
    TAG: str = 'tr'

    def td(self, content: Optional[str] = None) -> Union[HtmlObject, HtmlCell]:
        """Returns the cell, if a string is supplied, but an object, if an object is added"""
        return self.add(HtmlCell(content))

    def th(self, content: Union[str, Sequence[str]] = None) -> \
            Union[Union[HtmlCell, HtmlObject], Union[list[HtmlCell], list[HtmlObject]]]:
        """Create and add a new header cell object

        It is possible to pass along a list of objects or strings. This is sensible especially if you want to
        fill a row in a single path, e.g. header rows.
        :param content: May be the string contained in the cell or an object or a list of both
        :return: Returns the created cell or list of cells
        """
        if isinstance(content, list) or isinstance(content, tuple):
            return [self.add(HtmlHeadCell(content_piece)) for content_piece in content]
        else:
            return self.add(HtmlHeadCell(content))

    @property
    def cells(self) -> list[HtmlCell]:
        return self


class HtmlTable(HtmlContainer):
    TAG: str = 'table'

    column_styles = None

    def __init__(self):
        super().__init__()
        self._column_alignments = None

    def __str__(self):
        if self.css_styles:
            css_styles_str = ';'.join([key + ':' + value for key, value in self.css_styles.items()])
            self.tag_content['style'] = css_styles_str
        tag_content_str = ' '.join([f'{key}="{value}"' for key, value in self.tag_content.items()])
        return f'<{self.TAG} {tag_content_str}>{"".join([str(item) for item in self])}\n</{self.TAG}>\n'

    @property
    def header(self) -> Optional[HtmlRow]:
        return self[0] if len(self) > 0 else None

    @property
    def rows(self) -> Iterator[HtmlRow]:
        for row in self:
            yield row

    def tr(self):
        row = HtmlRow()
        self.add(row)
        return row

    def set_column_alignments(self, alignments: str):
        """Specify the alignments for contents in each column

        The alignments are given as a simple string with either c for center, l for left or r for right.
        :param alignments: A string containing the alignments, e.g. "clr"
        :return: None
        """
        for row in self:
            for i, alignment in enumerate(alignments):
                if i < len(row):  # FIXME: necessary?
                    row[i].css_styles["text-align"] = self.ALIGNMENT_MAP[alignment]
                else:
                    break


class ResultListing(HtmlContainer):
    """Display object that renders a tabular dataset (nested list) as a html table.

    :param content: a list like object to be displayed as a table
    :param mapping: a map of column names in the content to displayed
    :param show_all:
    :param rowcount_max:
    :param alignments:

    """

    table: HtmlTable
    content: Sequence
    columns_display: Sequence
    mapping: Mapping[str, str]

    def __init__(self, content: Sequence, mapping: Mapping[str, str] = None, show_all: bool = False,
                 rowcount_max: int = 200, alignments=None):
        """

        :param content:
        :param show_all:
        :param rowcount_max:
        :param alignments:
        """
        super().__init__()
        self.show_all = show_all
        self.content = content
        self.mapping = mapping if mapping else {}
        self.rowcount_max: int = rowcount_max
        self.columns_display = []

        tab: HtmlTable = super().table()
        self.table = tab
        headrow = tab.tr()
        if content:
            self.columns_display = self._derive_columnnames_for_display()
            if isinstance(content, dict):
                headrow.th("KEY")
                headrow.th("VALUE")
                for key, value in content.items():
                    tablerow = tab.tr()
                    tablerow.td(str(key))
                    tablerow.td(str(value))
                    # FIXME implement column names
            else:
                for key in self.columns_display:
                    if isinstance(mapping, dict):
                        headrow.th(self.mapping.get(key, key))
                    else:
                        headrow.th(key)
                for rownum, row in enumerate(content):
                    if rownum < rowcount_max:  # limitation of displayed rows
                        tablerow = tab.tr()
                        for key in self.columns_display:
                            try:
                                tablerow.td(str(row.get(key, '')))
                            except AttributeError:
                                try:
                                    tablerow.td(str(row[key]))
                                except KeyError:
                                    tablerow.td("")
                    else:
                        break
            if alignments:
                tab.set_column_alignments(alignments)
        else:
            pass  # no content, no rows

    def _derive_columnnames_for_display(self) -> list:
        if isinstance(self.content, dict):
            content_keys_data = self.content.keys()
        else:
            try:
                content_keys_data = self.content[0].keys()
            except:
                raise NotImplementedError(f"No implemented for content type {type(self.content)}")
        content_keys: MutableSequence[Any]
        if self.mapping:
            if not self.show_all:
                content_keys = [key for key in self.mapping if key in content_keys_data]
            else:
                content_keys = list(self.mapping)
                for key in content_keys_data:
                    if key not in self.mapping:
                        content_keys.append(key)
        else:
            content_keys = list(content_keys_data)
        return content_keys

    def __str__(self):
        # for row in self.table:
        #     for cell_nr, cell in enumerate(row):
        #         if cell_nr == 0:
        #             cell.css_styles['text-align'] = 'right'
        #     print (1)
        return ''.join([str(chunk) for chunk in self])


class ResultChoice(ResultListing):
    """Display object similar to ResultListing, but allows selection of rows

    :param content: a list like object to be displayed as a table
    :param listing_index: column name or sequence of names that identify a row
    :param row_selected: value, sequence or mapping of values for identification of a row
                         - if listing_index is just a string, then a string is expected
                         - if listing_index is a sequence, then either a sequence in the same order
                           or a mapping with the keys from the listing_index is expected.
    :param mapping: a map of column names in the content to displayed
    """

    PREFIX: str = '_rct_selected_'

    _index: Sequence[str]
    _row_selected: dict

    columns_config: dict[str, Any]

    def __init__(self, content: Sequence,
                 listing_index: Union[str, Sequence[str]],
                 row_selected: Union[str, Mapping, Sequence[Mapping]],
                 mapping: Mapping[str, str] = None,
                 show_all: bool = False,
                 rowcount_max: int = 200,
                 alignments: Optional[str] = None):
        """

        :param content:
        :param listing_index:
        :param row_selected:
        :param mapping:
        :param show_all:
        :param rowcount_max:
        :param alignments:
        """
        super().__init__(content, mapping, show_all, rowcount_max, alignments)
        self.listing_index = listing_index
        self.row_selected = row_selected
        self.columns_config: dict[str, Any] = {}
        self.columns_with_mappings: list = []

    @property
    def row_selected(self):
        return self._row_selected

    @row_selected.setter
    def row_selected(self, value):
        # either use a dictionary or set the given value as a dict.
        self._row_selected = None if not value else \
            value if isinstance(value, dict) or isinstance(value, list) else {self._index[0]: value}

    @property
    def listing_index(self) -> Sequence[str]:
        return self._index

    @listing_index.setter
    def listing_index(self, value):
        self._index = value if not isinstance(value, str) else [value, ]

    def compose(self):
        """Composes the final html composite object as a final step after all settings have been done."""
        parent_form: Optional[HtmlForm] = self.get_form()
        if not isinstance(parent_form, HtmlForm):
            raise Exception('ResultChoices have to be direct or indirect children of a form with an unique ID!')
        id_html_parentform: str = parent_form.id_html
        if not id_html_parentform:
            raise Exception("Only works if parent form has unique ID")
        if self.content:
            trigger_name = 'trigger_' + (self.id_html if self.id_html else 'result_choice')
            for index_col in self.listing_index:
                if index_col not in self.content[0]:  # TODO  rewrite with sets, rewrite with any or all
                    # (check if all have to apply)
                    raise Exception(
                        f"Listing_index '{index_col}' not in list content ({list(self.content[0].keys())})!")
            for i, row_dat in enumerate(self.content):
                if i < self.rowcount_max:
                    row: HtmlRow = self.table[i + 1]  # +1 for header
                    if isinstance(self.row_selected, list):
                        row.tag_content["onclick"] = f"entryMultiChoiceSetSelection('{id_html_parentform}', " \
                                                     f"'{self._index[0]}', '{row_dat[self._index[0]]}');"
                    else:
                        json = ",".join(f"'{index_col}':'{row_dat[index_col]}'" for index_col in self._index)
                        json += f",'{trigger_name}':'true'"
                        row.tag_content["onclick"] = f"entryChoiceSetSelection('{id_html_parentform}', {{{json}}});"
                    if self._is_selected_row(row_dat):
                        self._build_selected_row(row)
                    if self.columns_with_mappings:
                        for column_name in self.columns_with_mappings:
                            column_index = self.columns_display.index(column_name)
                            row[column_index][0] = self.columns_config[column_name]['codes'].get(row[column_index][0],
                                                                                                 row[column_index][0])
                else:
                    break
            for index_col in self.listing_index:
                if self.row_selected:
                    if isinstance(self.row_selected, list):
                        post_value = ";".join([str(row[index_col]) for row in self.row_selected])
                    else:
                        post_value = self.row_selected[index_col] if self.row_selected else None
                else:
                    post_value = None
                self.hidden(self.PREFIX + index_col,
                            value=post_value,
                            id_html=self.PREFIX + index_col)
            self.hidden(self.PREFIX + trigger_name,
                        value='false',
                        id_html=self.PREFIX + trigger_name)

    def _is_selected_row(self, row_dat: Mapping[str, Any]) -> bool:
        if not self.row_selected:
            return False
        elif isinstance(self.row_selected, str) \
                and str(row_dat.get(self.listing_index[0])) == self.row_selected:
            # simple input for one column index.
            return True
        elif isinstance(self.row_selected, list) \
                and any(all(str(row_dat.get(index_col)) == str(row_sel.get(index_col))
                            for index_col in self.listing_index)
                        for row_sel in self.row_selected):
            return True
        elif (isinstance(self.row_selected, dict) and
              all(str(row_dat[index_col]) == str(self.row_selected.get(index_col))
                  for index_col in self.listing_index)):
            return True
        else:
            return False

    def _build_selected_row(self, row):
        row.css_styles['color'] = 'white'
        row.css_styles['background'] = 'grey'

    def set_codes(self, column_name: str, codes: Union[Sequence, Mapping],
                  multichoice: bool = False, display_size: int = 1):
        """Assign a code mapping to a given column name.

        Codes/values within the column will be replaced by values from the mapping.
        All keys are converted to strings in order to simplify retrieval.

        :param column_name:
        :param codes:
        :param multichoice:
        :param display_size:
        :return:
        """
        if isinstance(codes, Mapping):
            self.columns_config.setdefault(column_name, {})['codes'] = {str(key): value for key, value in codes.items()}
            self.columns_with_mappings.append(column_name)
        else:
            self.columns_config.setdefault(column_name, {})['codes'] = codes
        self.columns_config[column_name]['multi_choice'] = multichoice
        self.columns_config[column_name]['display_size'] = display_size
        return self


class ResultEditor(ResultChoice):
    columns_protected: list[Any]

    def __init__(self, content: Sequence, listing_index, row_selected, mapping: Optional[Mapping[str, str]] = None,
                 show_all: bool = False, rowcount_max: int = 200, columns_protected: Optional[Sequence] = None,
                 alignments=None):
        super().__init__(content, listing_index, row_selected, mapping, show_all, rowcount_max, alignments)
        self.columns_protected = list(columns_protected) if columns_protected else []
        self.columns_protected.append(listing_index)

    def _build_selected_row(self, row):
        row.css_styles['color'] = 'white'
        row.css_styles['background'] = 'blue'
        row.tag_content.pop('onclick', None)
        for i, cell in enumerate(row):
            column_current = self.columns_display[i]
            if column_current not in self.columns_protected:
                cell_input = HtmlCell()
                if 'codes' in self.columns_config.get(column_current, {}):
                    cell_input.dropdown(name=column_current,
                                        var_input=cell[0] if cell else None,
                                        codes_source=self.columns_config[column_current]['codes'],
                                        missing_allowed=False)
                    if self.columns_config.get(column_current, {}).get('multi_choice'):
                        raise NotImplementedError
                    if self.columns_config.get(column_current, {}).get('display_size') != 1:
                        raise NotImplementedError
                else:
                    cell_input.textinput(column_current, var_input=cell[0] if cell else None)
                row[i] = cell_input
        cell_submit = row.td()
        button = cell_submit.submit('submit_save_resulteditor', 'save')  # focus on selected line
        button.tag_content['autofocus'] = 'autofocus'


class HtmlBody(HtmlContainer):
    TAG: str = 'body'


class HtmlHead(HtmlContainer):
    TAG: str = 'head'

    def resourcelink(self, rel: str, href: str, linktype: str = None) -> 'HtmlResource':
        """Add a link pointing to a resource for the header

        :param rel: which type of resource, e.g. "stylesheet"
        :param linktype: e.g. "text/css"
        :param href: path to file
        :return: HtmlResource
        """
        link = HtmlResource(rel=rel, href=href, linktype=linktype)
        self.add(link)
        return link


class HtmlPage:
    body: HtmlBody
    head: HtmlHead
    root_app = None

    def __init__(self, root_app=None):
        self.root_app = root_app
        self.head = HtmlHead()
        self.body = HtmlBody()

    @property
    def html(self):
        return '</?xml version="1.0" encoding="utf-8" ?>\n' \
               '<!DOCTYPE html>\n' \
               '<html xmlns="http://www.w3.org/1999/xhtml"' \
               f'xml:lang="de" lang="de">\n{self.head}\n' \
               f'{self.body}\n</html>\n'


class HtmlOptgroup(HtmlContainer):
    TAG: str = 'optgroup'


class HtmlOption(HtmlContainer):
    TAG: str = 'option'


class HtmlInput(HtmlObject):
    TAG: str = 'input'

    def __str__(self):
        if self.css_styles:
            self.tag_content['style'] = ";".join([f"{key}: {value}" for key, value in self.css_styles.items()])
        tag_content_str = ' '.join([f'{key}="{value}"' for key, value in self.tag_content.items()])
        return f'<{self.TAG} {tag_content_str}/>'


class HtmlH1(HtmlContainer):
    TAG: str = 'h1'

    def __init__(self, content=None, id_html: Optional[str] = None, class_html: Optional[str] = None):
        super().__init__(id_html, class_html)
        if content:
            self.add(content)


class HtmlH2(HtmlH1):
    TAG: str = 'h2'


class HtmlH3(HtmlH1):
    TAG: str = 'h3'


class HtmlP(HtmlContainer):
    TAG: str = 'p'

    def __init__(self, content=None, id_html: str = None, class_html: str = None):
        super().__init__(id_html=id_html, class_html=class_html)
        if content:
            self.append(content)


class HtmlLabel(HtmlContainer):
    TAG: str = 'label'

    def __init__(self, content: str = None, for_id: str = None, id_html: str = None, class_html: str = None):
        super().__init__(id_html=id_html, class_html=class_html)
        if content:
            self.append(content)
        if for_id:
            self.tag_content['for'] = for_id


class HtmlLink(HtmlContainer):
    TAG: str = 'a'

    def __init__(self, content: str = None, href: str = None, target: str = "_blank",
                 id_html: str = None, class_html: str = None):
        """
        If content is left empty, href will be taken instead.
        """
        super().__init__(id_html=id_html, class_html=class_html)
        if content:
            self.append(content)
        self.tag_content['href'] = href or content
        if target:
            self.tag_content['target'] = target


class HtmlResource(HtmlContainer):
    TAG: str = 'link'

    def __init__(self, rel: str, href: str, linktype: str = None):
        super().__init__()
        self.tag_content['href'] = href
        self.tag_content['rel'] = rel
        if linktype:
            self.tag_content['type'] = linktype


class HtmlSpan(HtmlContainer):
    TAG: str = 'span'

    def __init__(self, content=None, id_html: str = None, class_html: str = None):
        super().__init__(id_html=id_html, class_html=class_html)
        if content:
            self.append(content)
        if id_html:
            self.tag_content['id'] = id_html  # Fixme hide in setter


class HtmlDiv(HtmlContainer):
    TAG: str = 'div'

    def __init__(self, content=None, id_html: str = None, class_html: str = None):
        super().__init__(id_html=id_html, class_html=class_html)
        if content:
            self.append(content)


class HtmlForm(HtmlDiv):
    TAG: str = 'form'

    def __init__(self, id_html):
        super().__init__(id_html=id_html)
        self.tag_content['method'] = 'post'
        self.tag_content['action'] = ''


class HtmlScript(HtmlContainer):
    TAG: str = 'script'

    def __init__(self, content: str = None, src: str = None, script_type: str = None):
        super().__init__()
        self.script_type = script_type
        if content:
            self.add(content)
        if src:
            self.tag_content['src'] = src


class HtmlHidden(HtmlInput):
    def __init__(self, name: str, value: str = None, id_html: str = None):
        super().__init__(id_html=id_html)
        self.tag_content['type'] = 'hidden'
        self.tag_content['name'] = name
        if value:
            self.tag_content['value'] = value


class HtmlSubmit(HtmlInput):
    def __init__(self, name: Union[str, Enum], value=None, id_html: str = None, class_html=None):
        super().__init__(id_html=id_html, class_html=class_html)
        self.tag_content.update({'type': 'submit',
                                 'name': str(name)})
        if value:
            self.tag_content['value'] = value


class HtmlButton(HtmlInput):
    def __init__(self, name: str, value=None, id_html: str = None, class_html=None):
        super().__init__(id_html=id_html, class_html=class_html)
        self.tag_content.update({'type': 'button',
                                 'name': name})
        if value:
            self.tag_content['value'] = value


class HtmlTextInput(HtmlInput):
    def __init__(self, name: str, var_input=None, size: int = 20,
                 alignment: Optional[str] = None,
                 class_html: Optional[str] = None):
        super().__init__(class_html=class_html)
        self.tag_content.update({'type': 'text',
                                 'name': name,
                                 'size': size,
                                 'id': name})
        if var_input:
            self.tag_content['value'] = var_input
        if alignment:
            if alignment in self.ALIGNMENT_MAP:
                self.css_styles['text-align'] = self.ALIGNMENT_MAP[alignment]
            else:
                pass  # todo add debugging error


class HtmlPassword(HtmlInput):
    def __init__(self, name: str, var_input=None, size: int = 20):
        super().__init__()
        self.tag_content = {'type': 'password',
                            'name': name,
                            'size': size,
                            'id': name}
        if var_input:
            self.tag_content['value'] = var_input


class HtmlTextArea(HtmlInput):
    TAG: str = "textarea"

    def __init__(self, name: str, var_input=None, rows: int = 4, cols: int = 50):
        super().__init__()
        self.tag_content = {'name': name,
                            'cols': cols,
                            'rows': rows,
                            'id': name}
        self.var_input: str = var_input

    def __str__(self):
        tag_content_str = ' '.join([f'{key}="{value}"' for key, value in self.tag_content.items()])
        return f'<{self.TAG} {tag_content_str}>{self.var_input}</{self.TAG}>'


class HtmlRadio(HtmlInput):
    def __init__(self, name, var_input=None):
        super().__init__()
        self.tag_content = {'type': 'radio',
                            'name': name}
        if var_input:
            self.tag_content['value'] = var_input


class HtmlCheckbox(HtmlInput):
    def __init__(self, name, value, var_input: Union[int, str] = None, autosubmit: bool = False,
                 id_html: str = None, class_html: str = None):
        super().__init__(id_html, class_html)
        self.tag_content.update({'type': 'checkbox',
                                 'name': name,
                                 'value': value})
        if autosubmit:
            self.tag_content["onclick"] = "submit()"
        if str(var_input) == str(value):
            self.tag_content["checked"] = "checked"


class HtmlSelect(HtmlInput):
    TAG: str = "select"
    #: default code used for "no entry"-code
    _missing_code_id = -1
    #: default label used for "no entry"-code
    _missing_code_label = 'No Entry'

    codes_source: Union[MutableMapping, Sequence]

    def __init__(self, name: str, codes_source: Union[MutableMapping, Sequence],
                 var_input: Optional[Union[str, Sequence[str]]] = None, autosubmit: bool = False,
                 missing_allowed: bool = False, multiple: bool = False, size: int = 1,
                 optgroups: Optional[dict] = None):
        """Dropdown element for single or multiple selections

        :param codes_source:
        :param var_input:
        :param autosubmit:
        :param missing_allowed:
        :param multiple:
        :param size:
        :param optgroups:
        """
        super().__init__()
        self.tag_content = {'name': name}
        if isinstance(codes_source, Sequence):
            self.codes_source = dict(zip(codes_source, codes_source))
        else:
            self.codes_source = codes_source
        if isinstance(var_input, Sequence):
            self.var_input = list(map(str, var_input))
        else:
            try:
                if multiple:
                    self.var_input = var_input.get_list(name + "[]")
                else:
                    self.var_input = [str(var_input.get(name))]
            except AttributeError:
                self.var_input = [str(var_input)]
        self.autosubmit = autosubmit
        self.missing_allowed = missing_allowed
        self.multiple = multiple
        self.size = size
        self.optgroups = optgroups

    def __str__(self):
        if self.autosubmit:
            self.tag_content['onchange'] = 'submit()'
        if self.multiple:
            self.tag_content['multiple'] = 'multiple'
            self.tag_content['name'] += '[]'
            self.tag_content['size'] = self.size
        tag_content_str = ' '.join([f'{key}="{value}"' for key, value in self.tag_content.items()])
        codes_source_actual = self.codes_source if not self.missing_allowed else \
            {**{self._missing_code_id: self._missing_code_label}, **self.codes_source}

        content = []
        if self.optgroups:
            for key, value_list in self.optgroups.items():
                optgroup = HtmlOptgroup()
                optgroup.tag_content['label'] = key
                content.append(optgroup)
                for value in value_list:
                    label = codes_source_actual[value]
                    option = HtmlOption()
                    option.tag_content['value'] = value
                    if str(value) in self.var_input:
                        option.tag_content['selected'] = 'selected'
                    option.add(label)
                    optgroup.append(option)
        else:
            for code, label in codes_source_actual.items():
                option = HtmlOption()
                option.tag_content['value'] = code
                if str(code) in self.var_input:
                    option.tag_content['selected'] = 'selected'
                option.add(label)
                content.append(option)
        option_str = '\n'.join([str(obt).replace('\n', '') for obt in content])
        return f'<{self.TAG} {tag_content_str}>{option_str}\n</{self.TAG}>\n'


class RequestObject(Protocol):
    def get(self, *args, **kwargs): ...

    def form(self, *args, **kwargs): ...


class PySpassStorage:
    storage_object: RequestObject

    def get(self, field: str, default=None, noentry=None) -> Any:
        value = self.storage_object.get(field, default)
        return value if value != noentry else ""


class PySpassRequest(PySpassStorage):

    def __init__(self, request_object: RequestObject, framework: str):
        self.noentry_default = "-1"
        if framework.lower() == "flask":
            self.storage_object = request_object
        else:
            raise NotImplementedError

    def get(self, request_field: str, default=None, noentry=None) -> Any:
        value = self.storage_object.values.get(request_field, default)
        return value if value != noentry else ""

    def get_tuple(self, *args, default=None, noentry=None):
        return (self.get(arg, default=default, noentry=noentry) for arg in args)

    def get_int(self, request_field: str, default: int = None, noentry: int = None) -> Optional[int]:
        value = self.get(request_field, default=default, noentry=noentry)
        try:
            return int(value)
        except ValueError:
            return None

    def get_list(self, request_field: str) -> list:
        value_list = self.storage_object.form.getlist(request_field.strip("[]") + "[]")  # ensure closing brackets
        return value_list if isinstance(value_list, list) else [value_list]

    def get_float(self, request_field: str, default: float = None, noentry: float = None) -> Optional[float]:
        value = self.get(request_field, default=default, noentry=noentry)
        try:
            return float(value)
        except ValueError:
            return None


class PySpassSession(PySpassStorage):
    def __init__(self, session_object, framework: str):
        if framework.lower() == "flask":
            self.storage_object = session_object
        else:
            raise NotImplementedError

    def __setitem__(self, key, value):
        self.storage_object[key] = value


class PySpassRenderer:
    page: HtmlPage

    def __init__(self):
        self.page = HtmlPage()
        self.page.head.script(src='static/spass_forms.js')  # Fixme, make folder programatic


class PySpassApp(ABC):
    app_name: str
    logger: Logger = getLogger(__name__)
    page: HtmlPage
    session: PySpassSession
    request: PySpassRequest

    def __init__(self, app_name: str, request: PySpassRequest, session: PySpassSession):
        """

        :param app_name: distinct name for the action, also as seed for certain elements in form
        """
        self.app_name = app_name
        self.request = request
        self.session = session
        self.setup_page()

    def setup_page(self):
        self.logger.info("Setup page root")
        self.page = HtmlPage()
        self.page.head.script(src='static/spass_forms.js')  # Fixme, make folder programatic

    def display_login_form(self):
        self.logger.info("Display login form")
        div = self.page.body.div(id_html='centerBox')
        loginform = div.form("loginform")
        loginform.add("Username")
        username_entry = loginform.textinput(self.app_name + "_username_entry")
        username_entry.tag_content['placeholder'] = "username"
        loginform.add("Password")
        loginform.br()
        password_entry = loginform.password(self.app_name + "_password_entry")
        password_entry.tag_content['placeholder'] = "password"
        loginform.submit("submit_login", "enter")

    def resolve_login(self) -> bool:
        self.logger.info("Resolving login")
        if self.session.get("success_login"):
            self.logger.debug("Login already established")
            return True
        else:
            self.logger.debug("Login will be resolved")
            login_success: bool = False
            if self.request.get("submit_login"):
                login_success = self.affirm_credentials(self.request.get(self.app_name + "_username_entry"),
                                                        self.request.get(self.app_name + "_password_entry"))
            if login_success:
                self.session["success_login"] = True
                self.logger.debug("Login successful")
                return True
            else:
                self.display_login_form()
                return False

    @abstractmethod
    def affirm_credentials(self, username: str, password: str):
        self.logger.warning("Affirming credentials has to be implemented yet")
        return True
