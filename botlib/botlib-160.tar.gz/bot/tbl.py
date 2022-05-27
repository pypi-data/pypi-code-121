# This file is placed in the Public Domain.


"table"


def __dir__():
    return (
        "Table",
    )


class Table():

    mod = {}

    @staticmethod
    def add(o):
        Table.mod[o.__name__] = o

    @staticmethod
    def get(nm):
        return Table.mod.get(nm, None)
