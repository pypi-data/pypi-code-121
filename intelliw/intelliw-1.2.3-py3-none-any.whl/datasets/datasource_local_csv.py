import pandas as pd
import time

from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException
from intelliw.utils.global_val import gl
from intelliw.utils.logger import get_logger

logger = get_logger()

def try_read_file(filepath, nrows=None, skiprows=None):
    coding = ["utf8", "GB2312", "GBK", "GB18030", "utf-8-sig"]
    ok = False
    for c in coding:
        try:
            csv = pd.read_csv(filepath, nrows=nrows, skiprows=skiprows, encoding=c)
            ok = True
            break
        except UnicodeDecodeError:
            continue
    if not ok:
        raise UnicodeDecodeError(f"Can Not Encoding, Support Coding: {coding}")
    return csv

class DataSourceLocalCsv(AbstractDataSource):
    """
    本地 csv 文件数据源
    """

    def __init__(self, file_path):
        self.file_path = file_path
        self.__total = -1

    def total(self):
        if self.__total >= 0:
            return self.__total
        logger.info("start read files: %s", self.file_path)
        start_time = time.time()
        csv = try_read_file(self.file_path)
        self.__total = csv.index.size
        if self.__total == 0:
            logger.error('csv 文件为空')
            raise DataSourceReaderException('csv 文件为空')
        logger.info("total: %s, load time: %s",
                    self.__total, time.time() - start_time)
        return self.__total

    def reader(self, pagesize=10000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__DataSourceReaderLocalCsv(self.file_path, pagesize, offset, limit, transform_function)

    class __DataSourceReaderLocalCsv:
        """
        读取本地 csv
        """
        def __init__(self, file_path, pagesize=10000, offset=0, limit=0, transform_function=None):
            self.pagesize = pagesize
            self.is_stop = False
            self.file_path = file_path
            self.limit = limit
            self.meta = []         # csv 元数据
            self.read_count = 0
            self._init_meta()
            self.reader = self.__Reader(file_path, offset)

            self.transform_function = transform_function

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            if self.is_stop:
                raise StopIteration
            try:
                data = self._read_batch()
                return_data = {'result': data, 'meta': self.meta}
                if self.transform_function is not None:
                    return self.transform_function(return_data)
                return return_data
            except Exception as e:
                logger.exception("csv 文件读取错误")
                self.reader.close()
                raise DataSourceReaderException('csv 文件读取失败') from e

        def _read_batch(self):
            if self.limit > 0 and self.read_count + self.pagesize >= self.limit:
                batch_amount = self.limit - self.read_count
                self.is_stop = True
            else:
                batch_amount = self.pagesize
            batch = self.reader.read(batch_amount)
            self.read_count += batch_amount
            if self.reader.is_finish:
                self.is_stop = True
            return batch

        def _init_meta(self):
            csv = try_read_file(self.file_path, nrows=0)
            self.meta = [{'code': i} for i in csv.columns.values.tolist()]
            if type(gl.get("target_metadata")) is list:
                for m in gl.get("target_metadata"):
                    self.meta[m["target_col"]] = {'code': m["target_name"]}
            
        class __Reader:
            def __init__(self, file_path, offset=0):
                self.line_offset = offset
                self.is_finish = False
                self.file_path = file_path
               

            def read(self, amount=1):
                try:
                    self.csv = try_read_file(self.file_path, skiprows=self.line_offset)
                except pd.errors.EmptyDataError:
                    if self.line_offset == 0:
                        logger.error('csv 文件为空')
                        raise DataSourceReaderException('csv 文件为空')
                    else:
                        msg = '超出范围的 offset {}'.format(self.line_offset)
                        logger.error(msg)
                        raise DataSourceReaderException(msg)

                batch = []
                for i in range(amount):
                    try:
                        batch.append(self.csv.loc[i].values.tolist())
                    except (ValueError, KeyError) as e:
                        self.is_finish = True
                        self.line_offset += i
                        return batch
                self.line_offset += amount
                return batch
