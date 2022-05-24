'''
Author: Hexu
Date: 2022-04-25 15:16:48
LastEditors: Hexu
LastEditTime: 2022-05-20 10:01:23
FilePath: /iw-algo-fx/intelliw/datasets/datasource_iwimgdata.py
Description: 
'''
import json
import math
import os
import shutil
import requests
from urllib.error import HTTPError

from intelliw.config import config
from intelliw.datasets.datasource_base import AbstractDataSource, DataSourceReaderException
from intelliw.utils import iuap_request
from intelliw.utils.logger import get_logger

from concurrent.futures import ThreadPoolExecutor, as_completed


def err_handler(request, exception):
    print("请求出错,{}".format(exception))


class CocoProcess:
    coco_type = 3
    coco_config = None
    licenses = None
    info = None
    categories = None
    set_config = None

    @classmethod
    def set_coco_info(cls, instance):
        cls.info = instance['info']
        cls.licenses = instance['licenses']
        cls.categories = instance['categories']
        cls.coco_config = cls.__gen_config(
            instance['images'], instance['annotations'])
        cls.reset_config()
        
    @classmethod
    def reset_config(cls):
        cls.set_config = {'licenses':cls.licenses, 'info':cls.info, 'categories':cls.categories, 'images':[], 'annotations':[]}

    @classmethod
    def __gen_config(cls, images, annotations):
        amap = {a['image_id']: a for a in annotations}
        return {i['file_name']: {'image': i, 'annotation': amap[i['id']]} for i in images}
    
    @classmethod
    def gen_config(cls, filename):
        meta = cls.coco_config.get(filename)
        if meta == None:
            return f"image:{filename} annotation not exist"
        cls.set_config['images'].append(meta['image'])
        cls.set_config['annotations'].append(meta['annotation'])
        return None

    @classmethod
    def flush(cls, path):
        with open(path, 'w+') as fp:
            json.dump(cls.set_config, fp, ensure_ascii=False)    


class DataSourceIwImgData(AbstractDataSource):
    """
    非结构化存储数据源
    图片数据源
    """

    def __init__(self, input_address, get_row_address, ds_id, ds_type):
        """
        智能分析数据源
        :param input_address:   获取数据 url
        :param get_row_address: 获取数据总条数 url
        :param ds_id:   数据集Id
        """
        self.input_address = input_address
        self.get_row_address = get_row_address
        self.ds_id = ds_id
        self.ds_type = ds_type
        self.__gen_img_dir()

    def __gen_img_dir(self):
        logger = get_logger()
        filepath = os.path.join('./', config.CV_IMG_FILEPATH)
        if os.path.exists(filepath):
            logger.warn(f"图片数据保存路径存在:{filepath}, 正在删除路径内容")
            shutil.rmtree(filepath, ignore_errors=True)
        os.makedirs(config.CV_IMG_ANNOTATION_FILEPATH, 0o755, True)
        os.makedirs(config.CV_IMG_TRAIN_FILEPATH, 0o755, True)
        os.makedirs(config.CV_IMG_VAL_FILEPATH, 0o755, True)

    def total(self):
        logger = get_logger()
        params = {'dsId': self.ds_id, 'yTenantId': config.TENANT_ID}
        response = iuap_request.get(self.get_row_address, params=params)
        if 200 != response.status:
            msg = "获取行数失败，url: {}, response: {}".format(
                self.get_row_address, response)
            logger.error(msg)
            raise DataSourceReaderException(msg)

        row_data_str = response.body
        row_data = json.loads(row_data_str)
        data_num = row_data['data']

        if not isinstance(data_num, int):
            msg = "获取行数返回结果错误, response: {}, request_url: {}".format(
                row_data_str, self.get_row_address)
            logger.error(msg)
            raise DataSourceReaderException(msg)
        return data_num

    def reader(self, page_size=1000, offset=0, limit=0, transform_function=None, dataset_type='train_set'):
        return self.__Reader(self.input_address, self.ds_id, self.ds_type, self.total(), dataset_type, page_size, offset, limit, transform_function)

    class __Reader:
        def __init__(self, input_address, ds_id, ds_type, total, process_type, page_size=100, offset=0, limit=0, transform_function=None):
            """
            eg. 91 elements, page_size = 20, 5 pages as below:
            [0,19][20,39][40,59][60,79][80,90]
            offset 15, limit 30:
            [15,19][20,39][40,44]
            offset 10 limit 5:
            [10,14]
            """
            logger = get_logger()
            if offset > total:
                msg = "偏移量大于总条数:偏移 {}, 总条数: {}".format(offset, total)
                logger.error(msg)
                raise DataSourceReaderException(msg)
            self.input_address = input_address
            self.ds_id = ds_id
            self.ds_type = ds_type
            self.limit = limit
            self.offset = offset
            self.total = total
            if limit <= 0:
                self.limit = total - offset
            elif offset + limit > total:
                self.limit = total - offset
            self.page_size = page_size
            self.total_page = math.ceil(total / self.page_size)
            self.start_page = math.floor(offset / self.page_size)
            self.end_page = math.ceil((offset + self.limit) / page_size) - 1
            self.start_index_in_start_page = offset - self.start_page * page_size
            self.end_index_in_end_page = offset + self.limit - 1 - self.end_page * page_size
            self.current_page = self.start_page
            self.total_read = 0
            self.process_type = process_type
            self.transform_function = transform_function
            """
            print("total_page={},start_page={},end_page={},start_index={},end_index={},current_page={}"
                  .format(self.total_page,
                          self.start_page,
                          self.end_page,
                          self.start_index_in_start_page,
                          self.end_index_in_end_page,
                          self.current_page))
            """

        @property
        def iterable(self):
            return True

        def __iter__(self):
            return self

        def __next__(self):
            logger = get_logger()
            if self.current_page > self.end_page:
                logger.info('共读取原始数据 {} 条'.format(self.total_read))
                raise StopIteration
            try:
                page = self._read_page(self.current_page, self.page_size)
                if self.current_page == self.start_page or self.current_page == self.end_page:
                    # 首尾页需截取有效内容
                    start_index = 0
                    end_index = len(page['data']['content']) - 1
                    if self.current_page == self.start_page:
                        start_index = self.start_index_in_start_page
                    if self.current_page == self.end_page:
                        end_index = self.end_index_in_end_page
                    page['data']['content'] = page['data']['content'][start_index: end_index + 1]

                data = page['data']['content']
                self.current_page += 1
                self.total_read += len(data)
                return data
            except Exception as e:
                logger.exception(
                    "智能分析数据源读取失败, input_address: [{}]".format(self.ds_id))
                raise DataSourceReaderException('智能分析数据源读取失败') from e

        def _read_page(self, page_index, page_size):
            """
            调用智能分析接口，分页读取数据
            :param page_index: 页码，从 0 开始
            :param page_size:  每页大小
            :return:
            """
            request_data = {'dsId': self.ds_id, 'pageNumber': page_index,
                            'pageSize': page_size, 'yTenantId': config.TENANT_ID,
                            'type': self.ds_type}
            response = iuap_request.get(
                url=self.input_address, params=request_data)
            response.raise_for_status()
            return json.loads(response.body)

        def set_download(self, page):
            logger = get_logger()
            if self.ds_type == CocoProcess.coco_type:
                CocoProcess.reset_config()
                if CocoProcess.coco_config is None:
                    annotation_urls = page[0]['annotationUrl']
                    annotation = save_file(annotation_urls)
                    if annotation is None:
                        raise DataSourceReaderException(f'图片数据级标注信息有误，标注文件地址：{annotation_urls}')
                    annotation = json.loads(annotation)
                    CocoProcess.set_coco_info(annotation)

            errcount, successcount = 0,0
            with ThreadPoolExecutor(max_workers=os.cpu_count() * 2) as executor:
                futures = [executor.submit(self.__download, p) for p in page]
                for f in as_completed(futures):
                    try:
                        filename = f.result()
                        successcount += 1
                        print(f'[Framework Log] dataset download success: {filename}, now {successcount}, total {self.total}', end='\r')
                    except Exception as e:
                        errcount += 1
                        logger.error(f'dataset download error: {e}, total {errcount}')
            
            if self.ds_type == CocoProcess.coco_type:
                filename = self.process_type + ".json"
                CocoProcess.flush(os.path.join('.', config.CV_IMG_ANNOTATION_FILEPATH, filename))

        def __download(self, page):
            url = page['url']
            annotation_url = page['annotationUrl']
            filename = page['rowFileName']
            annotationname = filename.replace(
                page['fileNameType'], page['annotationType'])

            # 图片下载， 图片可能伴随特征工程
            process_file = config.CV_IMG_TRAIN_FILEPATH if self.process_type == 'train_set' else config.CV_IMG_VAL_FILEPATH
            filepath = os.path.join('.', process_file, filename)
            if save_file(url, filepath, self.transform_function) is None:
                raise HTTPError(f"image:{filename} download error")
            
            # 标注下载或写入内存
            if self.ds_type == CocoProcess.coco_type:
                err = CocoProcess.gen_config(filename)
                if err != None:
                    raise KeyError(f"CocoProcess.gen_config error: {err}")
            else:
                filepath = os.path.join('.', config.CV_IMG_ANNOTATION_FILEPATH, annotationname)
                if save_file(annotation_url, filepath) is None:
                    raise HTTPError(f"annotation:{annotationname} download error")
            
            return filename

        def __call__(self):
            abspath = os.path.abspath('.')
            return {'path':os.path.join(abspath, config.CV_IMG_FILEPATH), 'train_set':os.path.join(abspath, config.CV_IMG_TRAIN_FILEPATH),
            'val_set':os.path.join(abspath, config.CV_IMG_VAL_FILEPATH),'annotation':os.path.join(abspath, config.CV_IMG_ANNOTATION_FILEPATH)}



def save_file(url, filepath=None, transform_function=None):
    logger = get_logger()
    requests.packages.urllib3.disable_warnings()
    try:
        response = requests.get(url, verify=False)
        status = response.status_code
        if status == 200:
            data = response.content
            if transform_function:
                data = transform_function(data)
            if filepath:
                with open(filepath, 'wb') as fp:
                    fp.write(data)
                return filepath
            return data
        else:
            logger.error("http get url {} failed, status is {}".format(url, status))
            return None
    except requests.HTTPError as e:
        logger.error("http get url {} failed, error is {}".format(url, e))
        return None
