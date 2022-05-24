import json
import math
import time

from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException, AbstractDataSourceWriter, \
    DataSourceWriterException
from intelliw.utils import iuap_request
from intelliw.utils.logger import get_logger
from intelliw.utils.util import default_dump
from intelliw.config import config

logger = get_logger()


class DataSourceIntelliv(AbstractDataSource):
    """
    智能分析数据源
    """
    def __init__(self, input_address, get_row_address, input_model_id):
        """
        智能分析数据源
        :param input_address:   获取数据 url
        :param get_row_address: 获取数据总条数 url
        :param input_model_id:  读取的数据模型
        TODO add transformer
        TODO input_address = ${intelliv_host}/ds/model/result
        TODO get_row_address = ${intelliv_host}/ds/getRowCount/${input_model_id}/null
        """
        self.input_address = input_address
        self.get_row_address = get_row_address
        self.input_model_id = input_model_id

    def total(self):
        response = iuap_request.get(self.get_row_address)

        if 200 != response.status:
            msg = "获取行数失败，url: {}, response: {}".format(self.get_row_address, response)
            logger.error(msg)
            raise DataSourceReaderException(msg)

        row_data_str = response.body
        row_data = json.loads(row_data_str)
        data_num = row_data['data']

        if not isinstance(data_num, int):
            msg = "获取行数返回结果错误, response: {}, request_url: {}".format(row_data_str, self.get_row_address)
            logger.error(msg)
            raise DataSourceReaderException(msg)

        return data_num

    def reader(self, page_size=100000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__Reader(self.input_address, self.input_model_id, self.total(), page_size, offset, limit, transform_function)

    class __Reader:
        def __init__(self, input_address, input_model_id, total, page_size=10000, offset=0, limit=0, transform_function=None):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            self.input_address = input_address
            self.input_model_id = input_model_id
            self.limit = limit
            if limit <= 0:
                self.limit = total - offset
            elif offset + limit > total:
                self.limit = total - offset
            self.page_size = page_size if page_size < self.limit else self.limit
            self.total_page = math.ceil(total / self.page_size)
            self.start_page = math.ceil(offset / self.page_size) if offset > 0 else 1
            self.end_page = math.ceil((offset + self.limit) / page_size)
            self.start_index_in_start_page = offset - (self.start_page - 1) * page_size
            self.end_index_in_end_page = offset + self.limit - 1 - (self.end_page - 1) * page_size
            self.current_page = self.start_page

            self.transform_function = transform_function

            self.total_read = 0
            self.after_transform = 0

            self.meta = []

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            if self.current_page > self.end_page:
                logger.info('共读取原始数据 {} 条，经特征工程处理后数据有 {} 条'.format(self.total_read, self.after_transform))
                raise StopIteration
            try:
                page = self._read_page(self.current_page, self.page_size)

                if self.current_page == self.start_page or self.current_page == self.end_page:
                    # 首尾页需截取有效内容
                    start_index = 0
                    end_index = len(page['result']) - 1
                    if self.current_page == self.start_page:
                        start_index = self.start_index_in_start_page
                    if self.current_page == self.end_page:
                        end_index = self.end_index_in_end_page
                    page['result'] = page['result'][start_index: end_index + 1]

                page['meta'] = self.meta
                self.current_page += 1
                self.total_read += len(page['result'])
                if self.transform_function is not None:
                    transformed = self.transform_function(page)
                    self.after_transform += len(transformed['result'])
                    return transformed
                self.after_transform = self.total_read
                return page
            except Exception as e:
                logger.exception("智能分析数据源读取失败, input_address: [{}], model_id: [{}]".
                                 format(self.input_address, self.input_model_id))
                raise DataSourceReaderException('智能分析数据源读取失败') from e

        def _read_page(self, page_index, page_size):
            """
            调用智能分析接口，分页读取数据
            :param page_index: 页码，从 1 开始
            :param page_size:  每页大小
            :return:
            """
            request_data = {
                "modelId": self.input_model_id,
                "pager": {
                    "pageIndex": page_index,
                    "pageSize": page_size,
                    "pageCount": 0,
                    "recordCount": 0
                },
                "signDTO": {"ak": config.ACCESS_KEY,
                            "sign": config.ACCESS_SECRET,
                            "ts": int(time.time() * 1000)}
            }

            response = iuap_request.post_json(url=self.input_address, data=request_data)
            response.raise_for_status()

            return json.loads(response.body)


class DataSourceWriter(AbstractDataSourceWriter):
    def __init__(self, source_addr, dataSourceId, inferid, tenantId):
        self.source_addr = source_addr
        self.dataSourceId = dataSourceId
        self.inferid = inferid
        self.tenantId = tenantId

    def _get_data_hub_dest_cfg(self, starttime, endtime, data):
        data_dest = {
            "dataSourceId": self.dataSourceId,
            "serviceId": self.inferid,
            "startTime": starttime,
            "endTime": endtime,
            "tenantId": self.tenantId,
            'data': json.dumps(data, default=default_dump)
        }
        return data_dest

    def write(self, data, starttime):
        try:
            endtime = int(time.time() * 1000)
            result = self._get_data_hub_dest_cfg(starttime, endtime, data)
            res = iuap_request.post_json(url=self.source_addr, data=result)
            res.raise_for_status()
            res_data = json.loads(res.body)
            return res_data
        except Exception as e:
            logger.exception("写入数据错误")
            raise DataSourceWriterException('写入数据错误') from e