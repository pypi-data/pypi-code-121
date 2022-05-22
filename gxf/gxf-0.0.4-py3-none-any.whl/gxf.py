# -*- coding:utf-8 -*-

import pandas as pd


class GXFColmuns:
    _colmuns = [
        'chr_id',
        'source',
        'type',
        'start',
        'end',
        'score',
        'strand',
        'phase',
        'attributes'
    ]

    def __init__(self):
        for col in self._colmuns:
            self.__dict__[col] = col

    def __len__(self):
        return len(self._colmuns)

    def __iter__(self):
        return iter(self._colmuns)

    @property
    def columns(self):
        return self._colmuns


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

        df.iloc[:, 2] = df.iloc[:, 2].map(lambda x: str(x).lower())
        df.iloc[:, 6] = df.iloc[:, 6].map(self.strand)
        df[self.columns.strand] = df[self.columns.strand].astype(int)

        return df


class GXF:
    columns = GXFColmuns()

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
        elif type(filename) is pd.DataFrame:
            self.df = filename
        else:
            raise TypeError(
                'filename expect a str or GXFReader type, but got a %s' % type(filename))

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

        # bind method to new GXF class
        for col in self.columns:
            before = 'before_handle_%s' % col
            after = 'after_handle_%s' % col
            if hasattr(self, before):
                setattr(gxf, before, getattr(self, before))
            if hasattr(self, after):
                setattr(gxf, after, getattr(self, after))
        return gxf

    def filter(self, **kwargs):
        lambda_oper = {
            'gt': '>',
            'eq': '==',
            'ne': '!=',
            'lt': '<',
            'ge': '>=',
            'le': '<='
        }

        lambda_expr = []
        for k, v in kwargs.items():
            if '__' not in k:
                k = k + lambda_oper['eq']
            else:
                k, oper = k.split('__')
                if oper not in lambda_oper:
                    continue
                k = k + lambda_oper[oper]
            if isinstance(v, (int, float)):
                v = v
            if isinstance(v, str):
                v = '"' + v.strip("'").strip('"') + '"'
            lambda_expr.append('%s%s' % (k, v))
        query = '&'.join(lambda_expr)
        return self[query]

    def __getitem__(self, cond):
        self._do_handle('before')
        new_df = self.df.query(cond).reset_index(drop=True).copy()
        new_gxf = self._clone(new_df)
        new_gxf._do_handle('after')
        return new_gxf

    def __str__(self):
        return str(self.df)

    @property
    def dtypes(self):
        return self.df.dtypes

    def __len__(self):
        return self.df.shape[0]
