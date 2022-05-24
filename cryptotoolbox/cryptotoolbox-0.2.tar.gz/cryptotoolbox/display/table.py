#!/usr/bin/env python3
# coding: utf-8

""" Tools to display a table. """

# Built-in packages

# Third party packages

# Local packages

__all__ = ['set_table']


def set_table(matrix, columns, index):
    """ Display a table of size n x m.

    Parameters
    ----------
    matrix : array_like
        Array of shape (n, m).
    columns : list of str
        List of name of each column and of size m.
    index : list of str
        List of name of row and of size n.

    Returns
    -------
    str
        Table as string ready to print.

    """
    n, m = matrix.shape

    if len(index) != n or len(columns) != m:

        raise ValueError("Columns and index size ({}, {}) don't match with \
            matrix shape {} shape.".format(len(index), len(columns), (n, m)))

    elif n == 0 or m == 0:

        return ''

    # Set max size of cells of each columns
    index_len = max(len(i) for i in index)
    colum_len = [max(
        [len(matrix[i, j]) for i in range(n)] + [len(columns[j])]
    ) for j in range(m)]

    # Set head and boundary of table
    head = '| ' + ' ' * index_len
    bound = '+=' + '=' * index_len
    subound = '+-' + '-' * index_len

    generator_j = range(m)

    for c, j in zip(columns, generator_j):
        head += ' | ' + ' ' * (colum_len[j] - len(c)) + c
        bound += '=+=' + '=' * colum_len[j]
        subound += '-+-' + '-' * colum_len[j]

    head += ' |\n'
    bound += '=+\n'
    subound += '-+\n'

    # Set body of table
    body = ''
    for idx, i in zip(index, range(n)):
        body += '| ' + ' ' * (index_len - len(idx)) + idx

        for c, j in zip(matrix[i, :], generator_j):
            body += ' | ' + ' ' * (colum_len[j] - len(c)) + c
        body += ' |\n'

    return bound + head + subound + body + bound
