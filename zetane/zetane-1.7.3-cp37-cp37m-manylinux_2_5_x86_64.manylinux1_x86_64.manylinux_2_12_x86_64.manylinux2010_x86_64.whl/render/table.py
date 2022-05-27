

class Table:
    """The table object holds a reference to a table in the Zetane universe. It represents a dataframe in a visual, inspectable way.

    Args:
        filepath (str): Path to a tabular data file (.csv)

    Returns:
        Table: Returns a zetane Table object.
    """
    def __init__(self, nsocket, filepath=None):
        pass


    def header(self, header="infer", names=[]):
        """ Set the table headers.

        :param header: Row number(s) to use as the column names, and the start of the data.
                       Default behavior is to infer the column names: if no names are passed
                       the behavior is identical to header=0 and column names are inferred from
                       the first line of the file, if column names are passed explicitly then
                       the behavior is identical to header=None. Explicitly pass header=0 to be
                       able to replace existing names.
               names:  List of column names to use. If the file contains a header row, then you
                       should explicitly pass header=0 to override the column names.
        :return: self.
        """
        return self


    def column(self, usecols=[]):
        """ Set which columns to use.

        :param usecols: All elements must either be positional (i.e. integer indices into
                        the document columns) or strings that correspond to column names
                        provided either by the user in names or inferred from the document
                        header row. For example, a valid usecols parameter would be [0, 1, 2]
                        or ['foo', 'bar', 'baz']. An empty list will load all columns.
        :return: self.
        """
        return self


    def clone(self):
        """ 
            Clones this Table in Zetane; returns the cloned Table object

        Returns:
            Table: cloned from this Table.
        """
        return self
