import numpy as np
from lumipy.lab import Experiment, Convener


class StandardTests:

    def __init__(self, atlas, work_dir, n_parallel_set=None):
        self.atlas = atlas
        self.work_dir = work_dir
        self.n_parallel_set = (1, 5, 25, 50) if n_parallel_set is None else n_parallel_set

    def _reader_test(self, reader, n, x_max, name=None):
        work_dir = self.work_dir + '/readers'
        e = Experiment(lambda x: reader().select('*').limit(x), [1, x_max])
        name = reader.get_name() if name is None else name
        conveners = []

        for n_p in self.n_parallel_set:
            c = Convener(e, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            conveners.append(c)

        return conveners

    def _file_read_test(self, reader, test_data_path, n, x_max, name=None):
        work_dir = self.work_dir + '/readers'

        def fn(x):
            return reader(file=test_data_path, apply_limit=x).select('*')

        e = Experiment(fn, [1, x_max])
        name = reader.get_name() if name is None else name
        conveners = []

        for n_p in self.n_parallel_set:
            c = Convener(e, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            conveners.append(c)

        return conveners

    def _select_test(self, reader, n, x_max, m, name=None):
        work_dir = self.work_dir + '/core'
        name = reader.get_name() if name is None else name
        r = reader()
        cols = np.random.choice(r.get_columns(), m, replace=False)
        e = Experiment(lambda x: r.select(*cols).limit(x), [1, x_max])
        conveners = []

        for n_p in self.n_parallel_set:
            c = Convener(e, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            conveners.append(c)

        return conveners

    def _join_test(self, reader, n, x_max, m, name=None):
        work_dir = self.work_dir + '/core'
        name = reader.get_name() if name is None else name
        r = reader()

        def fn(x):
            a = r.with_alias('A').select('*').limit(x).to_table_var()
            b = r.with_alias('B').select('*').limit(x).to_table_var()
            a_cols = a.get_columns()[:m]
            b_cols = b.get_columns()[:m]
            join = a.left_join(b, on=b.i == a.i)
            return join.select(*(a_cols + b_cols))

        conveners = []
        e = Experiment(fn, [1, x_max])

        for n_p in self.n_parallel_set:
            c = Convener(e, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            conveners.append(c)

        return conveners

    def _writer_test(self, writer, test_data_path, n, x_max, name=None):
        work_dir = self.work_dir + '/writers'
        csv = self.atlas.drive_csv(file=test_data_path)
        name = writer.get_name() if name is None else name

        def baseline_fn(x):
            return csv.select('*').limit(1)

        def writer_fn(x):
            tv = csv.select('*').limit(x).to_table_var()
            return writer(to_write=tv).select('*')

        baseline_ex = Experiment(baseline_fn, [1, x_max])
        writer_ex = Experiment(writer_fn, [1, x_max])
        convener_pairs = []

        for n_p in self.n_parallel_set:
            baseline_cv = Convener(baseline_ex, work_dir, name + f'_baseline_NP{n_p}', n, n_parallel=n_p)
            writer_cv = Convener(writer_ex, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            convener_pairs.append((baseline_cv, writer_cv))

        return convener_pairs

    def _file_write_test(self, writer, file_type, n, x_max, name=None):
        work_dir = self.work_dir + '/writers'
        t = self.atlas.testing10m()
        name = writer.get_name() if name is None else name

        def baseline_fn(x):
            cols = np.random.choice(t.get_columns(), 50, replace=False)
            return t.select(*cols).limit(x)

        def writer_fn(x):
            cols = np.random.choice(t.get_columns(), 50, replace=False)
            tv = t.select(*cols).limit(x).to_table_var()
            return writer(tv, type=file_type, path='/honeycomb/testing/', file_names='luminesceTest').select('*')

        baseline_ex = Experiment(baseline_fn, [1, x_max])
        writer_ex = Experiment(writer_fn, [1, x_max])
        convener_pairs = []

        for n_p in self.n_parallel_set:
            baseline_cv = Convener(baseline_ex, work_dir, name + f'_baseline_NP{n_p}', n, n_parallel=n_p)
            writer_cv = Convener(writer_ex, work_dir, name + f'_NP{n_p}', n, n_parallel=n_p)
            convener_pairs.append((baseline_cv, writer_cv))

        return convener_pairs

    def transaction_read_test(self, n=100, x_max=10000):
        reader = self.atlas.lusid_portfolio_txn
        return self._reader_test(reader, n, x_max, name='transaction_read')

    def transaction_write_test(self, n=100, x_max=10000):
        writer = self.atlas.lusid_portfolio_txn_writer
        return self._writer_test(writer, '/honeycomb/testing/luminesceTransactionsTest100k.csv', n, x_max, name='transaction_write')

    def instrument_read_test(self, n=100, x_max=10000):
        reader = self.atlas.lusid_instrument
        return self._reader_test(reader, n, x_max, name='instrument_read')

    def instrument_write_test(self, n=100, x_max=10000):
        writer = self.atlas.lusid_instrument_equity_writer
        return self._writer_test(writer, '/honeycomb/testing/luminesceInstrumentsTest100k.csv', n, x_max, name='instrument_write')

    def holding_read_test(self, n=100, x_max=10000):
        reader = self.atlas.lusid_portfolio_holding
        return self._reader_test(reader, n, x_max, name='holding_read')

    def holding_write_test(self, n=100, x_max=10000):
        writer = self.atlas.lusid_portfolio_holding_writer
        return self._writer_test(writer, '/honeycomb/testing/luminesceHoldingsTest100k.csv', n, x_max, name='holding_write')

    def excel_read_test(self, n=100, x_max=10000, path="/honeycomb/testing/luminesceTest100k.xlsx"):
        reader = self.atlas.drive_excel
        return self._file_read_test(reader, path, n, x_max, name='excel_read')

    def csv_read_test(self, n=100, x_max=10000, path="/honeycomb/testing/luminesceTest100k.csv"):
        reader = self.atlas.drive_csv
        return self._file_read_test(reader, path, n, x_max, name='csv_read')

    def excel_write_test(self, n=100, x_max=10000):
        writer = self.atlas.drive_saveas
        return self._file_write_test(writer, 'Excel', n, x_max, name='excel_write')

    def csv_write_test(self, n=100, x_max=10000):
        writer = self.atlas.drive_saveas
        return self._file_write_test(writer, 'Csv', n, x_max, name='csv_write')

    # select n rows with m columns test
    def select_test(self, n=100, x_max=10000, m=5):
        return self._select_test(self.atlas.testing10m, n, x_max, m, name='select' + f'_{m}')

    # select n rows with m columns through a view test
    def select_view_test(self, n=100, x_max=10000, m=5):
        return self._select_test(self.atlas.testing10mview, n, x_max, m, name='select_view' + f'_{m}')

    # joint n rows with m columns test
    def join_test(self, n=100, x_max=10000, m=5):
        return self._join_test(self.atlas.testing10m, n, x_max, m, name='join' + f'_{m}')
