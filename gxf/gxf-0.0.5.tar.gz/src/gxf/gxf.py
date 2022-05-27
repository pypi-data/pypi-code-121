# -*- coding:utf-8 -*-

import enum
import pandas as pd

from .field import GXFColmuns
from .operator import make_query
from .util import (
    convert_to_gff,
    convert_to_gtf,
    green,
    red,
    register_method,
    split_by_double_dash
)

REGISTER = '__register'


class GXFType(enum.Enum):
    GTF = 0
    GFF = 1
    UNKNOWN = 3


class GXFReader:
    columns = GXFColmuns()
    strand = {
        '-': -1,
        '+': 1,
        1: '+',
        -1: '-'
    }

    def __init__(self, filename, **kwargs):
        self.filename = filename
        self.kwargs = kwargs
        self.df = self.handle_file()

    def handle_file(self):
        filename = self.filename
        df = pd.read_csv(
            filename,
            header=None,
            names=self.columns,
            skip_blank_lines=True,
            dtype={
                0: str,
                3: int,
                4: int,
            },
            **self.kwargs
        )

        return df


class GXF:
    columns = GXFColmuns()
    gxf_type = None

    def __init__(
        self,
        filename,
        comment='#',
        skiprows=0,
        sep='\t',
        read_cls=None
    ):
        self.comment = comment
        self.skiprows = skiprows
        self.sep = sep
        if read_cls is None:
            read_cls = GXFReader
        elif not isinstance(read_cls, GXFReader):
            raise TypeError('read_cls expected a %s, but got a %s',
                            type(GXFReader), type(read_cls))
        if type(filename) is str:
            self.df = read_cls(filename, **{
                'comment': comment,
                'skiprows': skiprows,
                'sep': sep
            }).df
        elif isinstance(filename, GXFReader):
            self.df = filename.df
        elif isinstance(filename, pd.DataFrame):
            self.df = filename
        else:
            raise TypeError(
                'filename expect a str or GXFReader type, but got a %s' % type(filename))
        if not len(self):
            self.gxf_type = GXFType.UNKNOWN
        else:
            self.gxf_type = GXFType.GFF if self.df.iloc[0, [-1]].map(
                lambda x: '=' in x
            ).any() else GXFType.GTF

    def _do_handle(self, where):
        for col in self.columns:
            handle_name = '%s_handle_%s' % (where, col)

            if hasattr(self, handle_name):
                handle = getattr(self, handle_name)
                self.df[col] = self.df[col].map(handle)

    def _clone(self, filename):
        gxf = GXF(
            filename,
            comment=self.comment,
            skiprows=self.skiprows,
            sep=self.sep
        )
        # # bind method to new GXF class
        # for col in self.columns:
        #     before = 'before_handle_%s' % col
        #     after = 'after_handle_%s' % col
        #     if hasattr(self, before):
        #         setattr(gxf, before, getattr(self, before))
        #     if hasattr(self, after):
        #         setattr(gxf, after, getattr(self, after))
        return gxf

    def filter(self, **kwargs):

        processes = []

        for k, v in kwargs.items():
            field_name, oper, when, handle = split_by_double_dash(k)
            if field_name not in self.columns:
                print()
                print('Only the following field names are supported.')
                for col in self.columns:
                    print('*: ' + green('%s' % col))
                print('But got: %s.' % red(field_name))
                exit(1)

            processes.append(make_query(field_name, oper, v, when, handle))

        # main process
        self._do_handle('before')
        new_df = self.df
        for process in processes:
            new_df = process(new_df)
        self._do_handle('after')


        return self._clone(new_df)

    def __str__(self):
        return str(self.df)

    @property
    def dtypes(self):
        return self.df.dtypes

    def to_dict(self):
        return self.df.to_dict('records')

    def __len__(self):
        return self.df.shape[0]

    def to_gff3(self, filename):
        if self.gxf_type != GXFType.GFF:
            self.df[self.columns.attributes] = self.df[self.columns.attributes].map(
                convert_to_gff)
        self.df.to_csv(
            filename,
            index=None,
            header=None,
            columns=self.columns,
            sep='\t',
        )

    def to_gtf(self, filename):
        if self.gxf_type != GXFType.GTF:
            self.df[self.columns.attributes] = self.df[self.columns.attributes].map(
                convert_to_gtf)
        file = open(filename, 'w', encoding='utf-8')
        for line in self.to_dict():
            line_str = []
            for col in self.columns:
                line_str.append(
                    str(line.get(col, ''))
                )
            file.write('\t'.join(line_str) + '\n')
        file.close()
