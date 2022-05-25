#-----------------------------
# -- fundb --
# cursor module
#-----------------------------

import copy
from math import ceil
from functools import reduce
from operator import itemgetter


class Cursor(object):

    def __init__(self, cursordat: list, sort=None, skip=None, limit=None):
        """Initialize the mongo iterable cursor with data"""
        self.cursordat = cursordat or []
        self.cursorpos = -1

        if len(self.cursordat) == 0:
            self.currentrec = None
        else:
            self.currentrec = self.cursordat[self.cursorpos]

        if sort:
            self.sort(sort)

        self.paginate(skip, limit)

    def __getitem__(self, key):
        """Gets record by index or value by key"""
        if isinstance(key, int):
            return self.cursordat[key]
        return self.currentrec[key]

    def paginate(self, skip, limit):
        """Paginate list of records"""
        if not self.count or not limit:
            return
        skip = skip or 0
        pages = int(ceil(self.count / float(limit)))
        limits = {}
        last = 0
        for i in range(pages):
            current = limit * i
            limits[last] = current
            last = current
        # example with count == 62
        # {0: 20, 20: 40, 40: 60, 60: 62}
        if limit and limit < self.count:
            limit = limits.get(skip, self.count)
            self.cursordat = self.cursordat[skip: limit]

    def _order(self, value, is_reverse=None):
        """Parsing data to a sortable form
        By giving each data type an ID(int), and assemble with the value
        into a sortable tuple.
        """

        def _dict_parser(dict_doc):
            """ dict ordered by:
            valueType_N -> key_N -> value_N
            """
            result = list()
            for key in dict_doc:
                data = self._order(dict_doc[key])
                res = (data[0], key, data[1])
                result.append(res)
            return tuple(result)

        def _list_parser(list_doc):
            """list will iter members to compare
            """
            result = list()
            for member in list_doc:
                result.append(self._order(member))
            return result

        # (TODO) include more data type
        if value is None or not isinstance(value, (dict,
                                                   list,
                                                   str,
                                                   bool,
                                                   float,
                                                   int)):
            # not support/sortable value type
            value = (0, None)

        elif isinstance(value, bool):
            value = (5, value)

        elif isinstance(value, (int, float)):
            value = (1, value)

        elif isinstance(value, str):
            value = (2, value)

        elif isinstance(value, dict):
            value = (3, _dict_parser(value))

        elif isinstance(value, list):
            if len(value) == 0:
                # [] less then None
                value = [(-1, [])]
            else:
                value = _list_parser(value)

            if is_reverse is not None:
                # list will firstly compare with other doc by it's smallest
                # or largest member
                value = max(value) if is_reverse else min(value)
            else:
                # if the smallest or largest member is a list
                # then compaer with it's sub-member in list index order
                value = (4, tuple(value))

        return value

    def sort(self, key_or_list, direction=None):
        """
        Sorts a cursor object based on the input
        :param key_or_list: a list/tuple containing the sort specification,
        i.e. ('user_number': -1), or a basestring
        :param direction: sorting direction, 1 or -1, needed if key_or_list
                          is a basestring
        :return:
        """

        # checking input format

        sort_specifier = list()
        if isinstance(key_or_list, list):
            if direction is not None:
                raise ValueError('direction can not be set separately '
                                 'if sorting by multiple fields.')
            for pair in key_or_list:
                if not (isinstance(pair, list) or isinstance(pair, tuple)):
                    raise TypeError('key pair should be a list or tuple.')
                if not len(pair) == 2:
                    raise ValueError('Need to be (key, direction) pair')
                if not isinstance(pair[0], str):
                    raise TypeError('first item in each key pair must '
                                    'be a string')
                if not isinstance(pair[1], int) or not abs(pair[1]) == 1:
                    raise TypeError('bad sort specification.')

            sort_specifier = key_or_list

        elif isinstance(key_or_list, str):
            if direction is not None:
                if not isinstance(direction, int) or not abs(direction) == 1:
                    raise TypeError('bad sort specification.')
            else:
                # default ASCENDING
                direction = 1

            sort_specifier = [(key_or_list, direction)]

        else:
            raise ValueError('Wrong input, pass a field name and a direction,'
                             ' or pass a list of (key, direction) pairs.')

        # sorting

        _cursordat = self.cursordat

        total = len(_cursordat)
        pre_sect_stack = list()
        for pair in sort_specifier:

            is_reverse = bool(1-pair[1])
            value_stack = list()
            for index, data in enumerate(_cursordat):

                # get field value

                not_found = None
                for key in pair[0].split('.'):
                    not_found = True

                    if isinstance(data, dict) and key in data:
                        data = copy.deepcopy(data[key])
                        not_found = False

                    elif isinstance(data, list):
                        if not is_reverse and len(data) == 1:
                            # MongoDB treat [{data}] as {data}
                            # when finding fields
                            if isinstance(data[0], dict) and key in data[0]:
                                data = copy.deepcopy(data[0][key])
                                not_found = False

                        elif is_reverse:
                            # MongoDB will keep finding field in reverse mode
                            for _d in data:
                                if isinstance(_d, dict) and key in _d:
                                    data = copy.deepcopy(_d[key])
                                    not_found = False
                                    break

                    if not_found:
                        break

                # parsing data for sorting

                if not_found:
                    # treat no match as None
                    data = None

                value = self._order(data, is_reverse)

                # read previous section
                pre_sect = pre_sect_stack[index] if pre_sect_stack else 0
                # inverse if in reverse mode
                # for keeping order as ASCENDING after sort
                pre_sect = (total - pre_sect) if is_reverse else pre_sect
                _ind = (total - index) if is_reverse else index

                value_stack.append((pre_sect, value, _ind))

            # sorting cursor data

            value_stack.sort(reverse=is_reverse)

            ordereddat = list()
            sect_stack = list()
            sect_id = -1
            last_dat = None
            for dat in value_stack:
                # restore if in reverse mode
                _ind = (total - dat[-1]) if is_reverse else dat[-1]
                ordereddat.append(_cursordat[_ind])

                # define section
                # maintain the sorting result in next level sorting
                if not dat[1] == last_dat:
                    sect_id += 1
                sect_stack.append(sect_id)
                last_dat = dat[1]

            # save result for next level sorting
            _cursordat = ordereddat
            pre_sect_stack = sect_stack

        # done

        self.cursordat = _cursordat

        return self

    def hasNext(self):
        """
        Returns True if the cursor has a next position, False if not
        :return:
        """
        cursor_pos = self.cursorpos + 1

        try:
            self.cursordat[cursor_pos]
            return True
        except IndexError:
            return False

    def next(self):
        """
        Returns the next record
        :return:
        """
        self.cursorpos += 1
        return self.cursordat[self.cursorpos]

    @property
    def count(self):
        """
        Returns the number of records in the current cursor
        :return: number of records
        """
        return len(self.cursordat)

