from collections import OrderedDict
from pathlib import Path
from typing import List, Union, Tuple

import numpy as np
import py2neo
from astropy.io import fits
from astropy.table import Table as AstropyTable, Row as AstropyRow, Column, vstack as astropy_vstack, MaskedColumn
import pandas as pd
from py2neo.cypher import Cursor
from tqdm import tqdm



class ColnameParser:
    def __init__(self, parent, partial_colname: str):
        self.parent = parent
        self.partial_colname = partial_colname

    def __getattr__(self, colname):
        return self.parent.__getattr__(self.partial_colname + '.' + colname)


class DotHandlerMixin:
    def __getattr__(self, attr):
        if attr in self.colnames:
            return self[attr]
        if any(colname.startswith(attr) for colname in self.colnames if '.' in colname):
            return ColnameParser(self, attr)
        return super(DotHandlerMixin, self).__getattr__(attr)


class Row(DotHandlerMixin, AstropyRow):
    pass


class Table(DotHandlerMixin, AstropyTable):  # allow using `.` to access columns
    Row = Row


class ArrayHolder:
    def __init__(self, array):
        self.array = array


def vstack_rows(rows: List[Tuple[List, List[bool], List[str]]], *args, **kwargs) -> Table:
    # for each column, remove null rows, make table, put nulls back in
    columns, names = zip(*rows)
    names = names[0]
    columns = list(zip(*columns))
    return Table([MaskedColumn(c, name=n) for c, n in zip(columns, names)])

def int_or_slice(x: Union[int, float, slice, None]) -> Union[int, slice]:
    if isinstance(x, (int, float)):
        return int(x)
    elif isinstance(x, slice):
        return x
    else:
        return slice(None, None)

class FileHandler:
    def __init__(self, rootdir: Union[Path, str], max_concurrency: int = 1000):
        self.rootdir = Path(rootdir)
        self.max_concurrency = max_concurrency
        self.files = OrderedDict()

    def read(self, filename: Union[Path, str], ext: Union[float, int, str] = None, index: Union[float, int, slice] = None,
             key: Union[str, int, float, slice] = None, header_only=False):
        f = self.open_file(filename)
        if ext is None:
            ext = 0
        ext = ext if isinstance(ext, str) else int(ext)
        hdu = f[ext]
        index = int_or_slice(index)
        key = key if isinstance(key, str) else int_or_slice(key)
        if header_only:
            if key is not None:
                return hdu.header[key]
            return hdu.header
        return hdu.data[index][key]


    def open_file(self, filename: Union[Path, str]):
        filename = self.rootdir / Path(filename)
        if filename in self.files:
            return self.files[filename]
        else:
            if len(self.files) >= self.max_concurrency:
                self.close_file(next(iter(self.files)))
            self.files[filename] = fits.open(str(filename), memmap=True)
            return self.files[filename]

    def close_file(self, filename: Path):
        if filename in self.files:
            del self.files[filename]

    def close_all(self):
        for filename in list(self.files):
            self.close_file(filename)

    def __del__(self):
        self.close_all()


class RowParser(FileHandler):
    def parse_product_row(self, row: py2neo.cypher.Record, names: List[Union[str, None]], is_products: List[bool],
                          as_row: bool):
        """
        Take a pandas dataframe and replace the structure of ['fname', 'extn', 'index', 'key', 'header_only']
        with the actual data
        """
        columns = []
        colnames = []
        for value, cypher_name, name, is_product in zip(row.values(), row.keys(), names, is_products):
            if is_product:
                if value is not None:
                    if isinstance(value[0], list):
                        value = value[0]
                    value = self.read(*value)
            name = cypher_name if name is None or name == 'None' else name
            mask = value is None or np.size(value) == 0
            try:
                mask |= np.all(~np.isfinite(value))
            except TypeError:
                pass
            if mask:
                value = np.ma.masked
            columns.append(value)
            colnames.append(name)
        if as_row:
            columns = [MaskedColumn([value], name=name) for value, name in zip(columns, names)]
            return Table(columns)[0]
        return columns, colnames

    def iterate_cursor(self, cursor: Cursor, names: List[Union[str, None]], is_products: List[bool], as_row: bool):
        for row in cursor:
            yield self.parse_product_row(row, names, is_products, as_row)

    def parse_to_table(self, cursor: Cursor, names: List[str], is_products: List[bool]):
        rows = list(self.iterate_cursor(cursor, names, is_products, False))
        if not rows:
            return Table([Column([], name=name) for name in names])
        return vstack_rows(rows)


if __name__ == '__main__':
    files = FileHandler(Path('/beegfs/car/weave/weaveio/'))
    r1 = files.read('L1/20160908/single_1002213.fit', ext=-1, index=slice(0, 10), key='SNR')
    r2 = files.read('L1/20160908/single_1002213.fit', ext=-1, index=slice(0, 6), key='SNR')
    print(r1)