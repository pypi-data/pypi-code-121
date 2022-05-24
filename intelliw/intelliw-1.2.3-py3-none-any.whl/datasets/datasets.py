from copy import deepcopy
import math
import random
from abc import ABCMeta, abstractmethod
from collections.abc import Iterable

from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceEmpty, AbstractDataSourceWriter, \
    EmptyDataSourceWriter
from intelliw.datasets.datasource_local_csv import DataSourceLocalCsv
from intelliw.utils.logger import get_logger
from intelliw.config import config
from intelliw.utils.global_val import gl
from intelliw.utils.exception import DatasetException

logger = get_logger()


class DataSourceType:
    '''输入数据源类型'''
    EMPTY = 0   # 空
    REMOTE_CSV = 1  # 远程csv
    INTELLIV = 2  # 智能分析
    LOCAL_CSV = 3  # 本地 csv
    IW_IMAGE_DATA = 4  # 图片数据源
    IW_FACTORY_DATA = 5  # 数据工场数据集

class DatasetType:
    TRAIN = 'train_set'
    VALID = 'validation_set'


def get_datasource(intelliv_src: str, intelliv_row_addr: str) -> AbstractDataSource:
    datasource_type = config.SOURCE_TYPE
    if datasource_type == DataSourceType.EMPTY:
        return DataSourceEmpty()
    elif datasource_type == DataSourceType.REMOTE_CSV:
        from intelliw.datasets.datasource_remote_csv import DataSourceRemoteCsv
        return DataSourceRemoteCsv(config.DATA_SOURCE_ADDRESS)
    elif datasource_type == DataSourceType.INTELLIV:
        from intelliw.datasets.datasource_intelliv import DataSourceIntelliv
        return DataSourceIntelliv(intelliv_src, intelliv_row_addr, config.INPUT_MODEL_ID)
    elif datasource_type == DataSourceType.LOCAL_CSV:
        return DataSourceLocalCsv(config.CSV_PATH)
    elif datasource_type == DataSourceType.IW_IMAGE_DATA:
        from intelliw.datasets.datasource_iwimgdata import DataSourceIwImgData
        return DataSourceIwImgData(intelliv_src, intelliv_row_addr, config.INPUT_DATA_SOURCE_ID, config.INPUT_DATA_SOURCE_TRAIN_TYPE)
    elif datasource_type == DataSourceType.IW_FACTORY_DATA:
        from intelliw.datasets.datasource_iwfactorydata import DataSourceIwFactoryData
        return DataSourceIwFactoryData(intelliv_src, intelliv_row_addr, config.INPUT_DATA_SOURCE_ID)
    else:
        err_msg = "数据读取失败，无效的数据源类型: {}".format(datasource_type)
        logger.error(err_msg)
        raise ValueError(err_msg)


def get_datasource_writer(output_addr: str) -> AbstractDataSourceWriter:
    output_datasource_type = config.OUTPUT_SOURCE_TYPE
    if output_datasource_type == DataSourceType.EMPTY:
        return EmptyDataSourceWriter()
    elif output_datasource_type == DataSourceType.INTELLIV or output_datasource_type == DataSourceType.IW_FACTORY_DATA:
        from intelliw.datasets.datasource_intelliv import DataSourceWriter
        return DataSourceWriter(output_addr, config.OUTPUT_DATA_SOURCE_ID, config.INFER_ID, config.TENANT_ID)
    else:
        err_msg = "输出数据源设置失败，无效的数据源类型: {}".format(output_datasource_type)
        logger.error(err_msg)
        raise ValueError(err_msg)


class DataSets:
    def __init__(self, datasource: AbstractDataSource, config):
        self.datasource = datasource
        self.train_ratio = config.TRAIN_DATASET_RATIO

        if config.DATA_SPLIT_MODE == 0:
            spliter_cls = SequentialSpliter
        elif config.DATA_SPLIT_MODE == 1:
            spliter_cls = ShuffleSpliter
        elif config.DATA_SPLIT_MODE == 2:
            spliter_cls = TargetRandomSpliter
        elif config.DATA_SPLIT_MODE == 3:
            spliter_cls = RandomSpliter
        else:
            err_msg = "输出数据源设置失败，数据集划分模式: {}".format(config.DATA_SPLIT_MODE)
            logger.error(err_msg)
            raise ValueError(err_msg)

        read_size = config.DATA_SOURCE_READ_SIZE if config.DATA_SOURCE_READ_SIZE > 0 else 10000

        self.spliter = spliter_cls(datasource, config.TRAIN_DATASET_RATIO, config.VALID_DATASET_RATIO,
                                   read_size, config.DATA_SOURCE_READ_LIMIT)

    def empty_reader(self,dataset_type=DatasetType.TRAIN):
        return self.datasource.reader(page_size=1, offset=0, limit=0, transform_function=None, dataset_type=dataset_type)

    def reader(self, page_size=100000, offset=0, limit=0, split_transform_function=None):
        return self.datasource.reader(page_size, offset, limit, split_transform_function)

    def train_reader(self, split_transform_function=None, alldata_transform_function=None, feature_process=None):
        data = self.spliter.train_reader(split_transform_function)
        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
            alldata = DataSets.read_all(data)
            reader = self.empty_reader(DatasetType.TRAIN)
            reader.set_download(alldata)
            return reader()
        elif alldata_transform_function or feature_process:
            # 这两种方法需要全部数据， 第一步获取全部数据
            alldata = DataSets.read_all(data)
            if alldata_transform_function:
                alldata = alldata_transform_function(alldata)
            if feature_process:
                alldata = feature_process(alldata, DatasetType.TRAIN)
            return [alldata]
        return data

    def validation_reader(self, split_transform_function=None, alldata_transform_function=None, feature_process=None):
        data = self.spliter.validation_reader(split_transform_function)
        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
            alldata = DataSets.read_all(data)
            reader = self.empty_reader(DatasetType.VALID)
            reader.set_download(alldata)
            return reader()
        elif alldata_transform_function or feature_process:
            # 这两种方法需要全部数据， 第一步获取全部数据
            alldata = DataSets.read_all(data)
            if alldata_transform_function:
                alldata = alldata_transform_function(alldata)
            if feature_process:
                alldata = feature_process(alldata, DatasetType.VALID)
            return [alldata]
        return data

    @classmethod
    def read_all(cls, reader:Iterable) -> Iterable:
        # 图片数据为图片信息 其他数据集为{"result": , "meta": }
        alldata = dict() if config.SOURCE_TYPE != DataSourceType.IW_IMAGE_DATA else list()
        for data in reader:
            if config.SOURCE_TYPE != DataSourceType.IW_IMAGE_DATA:
                if not alldata:
                    alldata = data
                elif 'result' in data and 'result' in alldata:
                    alldata['result'] = alldata['result'] + data['result']
            else:
                alldata.extend(data)         
        return alldata

    @classmethod
    def get_col_list(cls, reader:Iterable) -> list:
        # 图片数据为列表 其他数据集为{"result": , "meta": }
        col_list = list()
        copy_reader = deepcopy(reader)
        for data in copy_reader:
            if config.SOURCE_TYPE != DataSourceType.IW_IMAGE_DATA:
                col_list = [i["code"]  for i in data["meta"]]
            break
        return col_list

def get_dataset(intelliv_src: str, intelliv_row_addr: str) -> DataSets:
    datasource = get_datasource(intelliv_src, intelliv_row_addr)
    return DataSets(datasource, config)


class DataSetSpliter(metaclass=ABCMeta):
    def __init__(self, datasource: AbstractDataSource, train_ratio, valid_ratio, read_size, read_limit):
        if not isinstance(datasource, AbstractDataSource):
            raise TypeError("data_source has a wrong type, required: AbstractDataSource, actually: {}"
                            .format(type(datasource).__name__))
        assert 0 < train_ratio <= 1
        assert 0 <= valid_ratio < 1
        assert read_size > 0

        self.datasource = datasource
        self.data_num = datasource.total()

        if read_limit == 0:
            self.total_read = self.data_num
        elif self.data_num > read_limit:
            self.total_read = read_limit
        else:
            self.total_read = self.data_num

        self.read_size = read_size
        if self.read_size > self.total_read:
            self.read_size = self.total_read

        self.train_num = math.floor(self.total_read * float(train_ratio))
        self.valid_num = self.total_read - self.train_num

    def train_reader(self, transform_function=None) -> Iterable:
        if self.train_num == 0:
            return DataSourceEmpty().reader()
        return self._train_reader(transform_function)

    @abstractmethod
    def _train_reader(self, transform_function=None) -> Iterable:
        pass

    def validation_reader(self, transform_function=None) -> Iterable:
        if self.valid_num == 0:
            return DataSourceEmpty().reader()
        return self._validation_reader(transform_function)

    @abstractmethod
    def _validation_reader(self, transform_function=None) -> Iterable:
        pass

# SequentialSpliter 顺序读取数据
class SequentialSpliter(DataSetSpliter):
    """顺序读取数据
    数据按照训练集比例分割，前面为训练集，后面为验证集
    """    
    def __init__(self, datasource: AbstractDataSource, train_ratio, valid_ratio, read_size, read_limit):
        super().__init__(datasource, train_ratio, valid_ratio, read_size, read_limit)

    def _train_reader(self, transform_function=None):
        batch_size = self.read_size if self.read_size < self.train_num else self.train_num
        return self.datasource.reader(batch_size, 0, self.train_num, transform_function, DatasetType.TRAIN)

    def _validation_reader(self, transform_function=None):
        batch_size = self.read_size if self.read_size < self.valid_num else self.valid_num
        return self.datasource.reader(batch_size, self.train_num, self.valid_num, transform_function, DatasetType.VALID)

# RandomSpliter 局部乱序读取
class RandomSpliter(DataSetSpliter):
    """局部乱序读取
    生成与切片长度相等的[]bool, 其中按照训练集比例生成等比True和False, 并打乱顺序
    后续的切片遍历以此列表为索引，分割数据集和验证集
    mask = [Ture, False, True, True, True, False...], len(mask) = 总数据量 if 总数据量 < 10000 else 1000
    True代表训练集数据, False代表验证集数据, 以此进行数据遍历
    """
    def __init__(self, datasource: AbstractDataSource, train_ratio, valid_ratio, read_size, read_limit):
        super().__init__(datasource, train_ratio, valid_ratio, read_size, read_limit)
        # 使用固定 seed 保证同一个数据集多次读取划分一致
        r = random.Random(1024)
        self.__mask = RandomSpliter.__build_mask(
            r, self.total_read, train_ratio)

    def _train_reader(self, transform_function=None) -> Iterable:
        train_musk_func = RandomSpliter.__mask_func(self.__mask, True)
        masked_transform = RandomSpliter.__masked_transform(
            train_musk_func, transform_function)
        return self.datasource.reader(self.read_size, 0, self.total_read, masked_transform, DatasetType.TRAIN)

    def _validation_reader(self, transform_function=None) -> Iterable:
        validation_musk_func = RandomSpliter.__mask_func(self.__mask, False)
        masked_transform = RandomSpliter.__masked_transform(
            validation_musk_func, transform_function)
        return self.datasource.reader(self.read_size, 0, self.total_read, masked_transform, DatasetType.VALID)

    @staticmethod
    def __masked_transform(mask_func, transform_function=None):
        def transform(result):
            result['result'] = mask_func(result['result'])
            if transform_function is not None:
                result = transform_function(result)
            return result
        return transform

    @staticmethod
    def __build_mask(r: random.Random, total_num: int, train_ratio: float):
        mask_size = total_num if total_num < 10000 else 1000
        mask = [False for _ in range(mask_size)]
        true_num = math.floor(len(mask) * train_ratio)
        for i in range(true_num):
            mask[i] = True
        r.shuffle(mask)
        return mask

    @staticmethod
    def __mask_func(mask: list, is_train: bool):
        index = [0]
        def func(data):
            res = []
            for val in data:
                if mask[index[0]] == is_train:
                    res.append(val)
                index[0] = index[0] + 1
                if index[0] >= len(mask):
                    index[0] = 0
            return res
        return func

# TargetRandomSpliter 根据目标列乱序读取
class TargetRandomSpliter(DataSetSpliter):
    """根据目标列乱序读取
    按照目标列中类别的比例，进行训练集和验证集的划分，保证训练集和验证集中类别比例与整体数据比例相同
    
    使用此方法的前提：
     - 有目标列
     - 是分类
    
    几种可能存在的边界：
     - 分类太多: 1w数据分出来5k类别, 算法框架在tag_count/total > 0.5的时候会warn
     - 类别唯一: 只有一个tag
     - 某类别唯一: 某个tag只有一
     - 无目标列下标: 需要配置targetCol
     - 训练集或验证集比例为1

    注意:
    此方法需要读取全部数据，会给内存带来压力
    """
    def __init__(self, datasource: AbstractDataSource, train_ratio, valid_ratio, read_size, read_limit):
        super().__init__(datasource, train_ratio, valid_ratio, read_size, read_limit)
        
        self.target_col = None
        self.train_data = None
        self.valid_data = None
        self.seed = 1024 # 使用固定 seed 保证同一个数据集多次读取划分一致
        self.train_ratio = train_ratio
        self.batch_size = self.read_size if self.read_size < self.total_read else self.total_read
        self._verify()

    def _verify(self):
        target_metadata = gl.get("target_metadata")
        if target_metadata is None or len(target_metadata) == 0:
            raise DatasetException("配置文件(algorithm.yaml)中未设置target相关数据")
        if len(target_metadata) > 1:
            raise DatasetException("目前只支持针对单目标列的数据shuffle处理")
        self.target_col = target_metadata[0]["target_col"]
        if type(self.target_col) != int:
            raise DatasetException(f"类型错误:targetCol类型应为int, 当前数据: {self.target_col}-{type(self.target_col)}")
        if self.train_ratio in (0, 1):
            raise DatasetException("根据目标列乱序读取,train_ratio不应设置为1或者0")
    
    def _train_reader(self, transform_function=None):
        if self.train_data is None:
            self._set_data(transform_function) 
        return self.train_data
            
    def _validation_reader(self, transform_function=None):
        if self.valid_data is None:
            self._set_data(transform_function) 
        return self.valid_data

    def _set_data(self, transform_function=None):
        import pandas as pd

        # 获取所有数据
        reader = self.datasource.reader(self.batch_size, 0, self.train_num, transform_function)
        alldata = DataSets.read_all(reader)
        meta = alldata["meta"]
        rawdata = alldata["result"]

        df = pd.DataFrame(rawdata)
        
        # 边界处理
        if df.shape[1] < self.target_col+1:
            raise DatasetException(f"数据集不存在目标列, 数据集列数{df.shape[1]}, 目标列下标{self.target_col}")
        
        train, valid = pd.DataFrame() ,pd.DataFrame()                       
        tags = df[df.columns[self.target_col]].unique().tolist() 
        tag_count = len(tags)

        # 边界处理
        if (tag_count < 2) or (tag_count<<1 >= self.total_read):
            raise DatasetException("目标列类别数量唯一, 或者类别数量超过总数据的50%")

        for tag in tags:
            data = df[df[df.columns[self.target_col]] == tag]

            # 边界处理
            if data.shape[0] == 1:
                raise DatasetException(f"tag: {tag} 只有一条数据")
            
            sample = data.sample(int(self.train_ratio*len(data)), random_state=self.seed)
            sample_index = sample.index

            all_index = data.index
            residue_index = all_index.difference(sample_index) # 去除sample之后剩余的数据
            residue = data.loc[residue_index] 

            train = pd.concat([train, sample], ignore_index=True)
            valid = pd.concat([valid, residue], ignore_index=True)

        self.train_data = [{"meta":meta, "result":train.values.tolist()}]
        self.valid_data = [{"meta":meta, "result":valid.values.tolist()}]

        
# ShuffleSpliter 乱序读取
class ShuffleSpliter(DataSetSpliter):
    """乱序读取
   
    注意:
    此方法需要读取全部数据，会给内存带来压力
    """
    def __init__(self, datasource: AbstractDataSource, train_ratio, valid_ratio, read_size, read_limit):
        super().__init__(datasource, train_ratio, valid_ratio, read_size, read_limit)
        
        self.train_data = None
        self.valid_data = None
        self.seed = 1024 # 使用固定 seed 保证同一个数据集多次读取划分一致
        self.batch_size = self.read_size if self.read_size < self.total_read else self.total_read

    def _train_reader(self, transform_function=None):
        if self.train_data is None:
            self._set_data(transform_function) 
        return self.train_data
            
    def _validation_reader(self, transform_function=None):
        if self.valid_data is None:
            self._set_data(transform_function) 
        return self.valid_data

    def _set_data(self, transform_function=None):
        # 获取所有数据
        r = random.Random(1024)
        reader = self.datasource.reader(self.batch_size, 0, self.total_read, transform_function)
        alldata = DataSets.read_all(reader)
        
        if config.SOURCE_TYPE == DataSourceType.IW_IMAGE_DATA:
            r.shuffle(alldata)
            self.train_data = [alldata[:self.train_num]]
            self.valid_data = [alldata[self.train_num:]]
        else:
            meta = alldata.pop("meta")
            rawdata = alldata.pop("result")
            r.shuffle(rawdata)
            self.train_data = [{"meta":meta, "result":rawdata[:self.train_num]}]
            self.valid_data = [{"meta":meta, "result":rawdata[self.train_num:]}]
    
        