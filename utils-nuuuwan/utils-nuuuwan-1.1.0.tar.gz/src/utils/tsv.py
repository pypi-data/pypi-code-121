"""Utils for reading and writing Tab-Seperated Variable (TSV) files.

The default tab delimiter can be overridden,
    by passing a *delimiter* parameter to *read* and *write*.

.. code-block:: python

    >>> import utils.tsv
    >>> data = [{'name': 'Alice', 'age': '20'}]
    >>> file_name = '/tmp/data.tsv'
    >>> utils.tsv.write(file_name, data)
    >>> data2 = utils.tsv.read(file_name)
    >>> data == data2
    True
"""

import csv

from utils import filex

DEFAULT_DELIMITER = '\t'
DIALECT = 'excel'
NULL_VALUE = ''


def _get_field_names_from_dict_list(dict_list):
    """_get_field_names_from_dict_list."""
    return list(dict_list[0].keys())


def _read_helper(
    csv_lines,
    delimiter=DEFAULT_DELIMITER,
):
    """Read from xsv file handle, and output dict list."""
    dict_list = []
    field_names = None
    reader = csv.reader(
        csv_lines,
        dialect=DIALECT,
        delimiter=delimiter,
    )
    for row in reader:
        if not field_names:
            field_names = row
        else:
            datum = dict(
                zip(
                    field_names,
                    row,
                )
            )
            if datum:
                dict_list.append(datum)
    return dict_list


def read(
    file_name,
    delimiter=DEFAULT_DELIMITER,
):
    """Read file."""
    csv_lines = filex.read(file_name).split('\n')
    return _read_helper(csv_lines, delimiter)


def write(
    file_name,
    dict_list,
    delimiter=DEFAULT_DELIMITER,
):
    """Write dict_list to file."""
    with open(file_name, 'w') as fout:
        writer = csv.writer(
            fout,
            dialect=DIALECT,
            delimiter=delimiter,
        )

        field_names = _get_field_names_from_dict_list(dict_list)
        writer.writerow(field_names)
        writer.writerows(
            list(
                map(
                    lambda d: list(
                        map(
                            lambda field_name: d.get(field_name, NULL_VALUE),
                            field_names,
                        )
                    ),
                    dict_list,
                )
            ),
        )
        fout.close()
