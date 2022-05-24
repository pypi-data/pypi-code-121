#!/usr/bin/env python
# coding: utf-8
import json
import time
import traceback

from intelliw.datasets.datasets import DataSets, get_dataset, get_datasource_writer
from intelliw.core.report import RestReport
from intelliw.core.trainer import Trainer
from intelliw.core.infer import Infer
import intelliw.utils.message as message
from intelliw.datasets.datasource_base import *
from intelliw.utils.util import default_dump
from intelliw.config import config

logger = get_logger()

batchjob_infer = "batchjob-infer"
batchjob_train = "batchjob-train"


def get_batch_msg(issuccess, starttime, msg):
    """
    批处理上报信息，inferTaskStatus 不为空，会被记录为一次调用，标识一次批处理的状态
    """
    outmsg = [
        {
            'status': 'start',
            'inferid': config.INFER_ID,
            'instanceid': config.INSTANCE_ID,
            'inferTaskStatus': [
                {
                    "id": config.INFER_ID,
                    "issuccess": issuccess,
                    "starttime": starttime,
                    "endtime": int(time.time() * 1000),
                    "message": msg
                }
            ]
        }
    ]
    return outmsg


def get_msg(is_success, msg):
    """
    批处理上报信息，inferTaskStatus 为空，不会被记录为一次调用，用于上报和单次调用无关的消息
    """
    return [
        {
            'status': 'start',
            'inferid': config.INFER_ID,
            'instanceid': config.INSTANCE_ID,
            'inferTaskStatus': []
        }
    ]


def validate_batch_job(reporter, path, task):
    if task == 'infer':
        Infer(path, reporter)
        msg = get_msg(True, '定时推理校验通过，上线成功')
        reporter.report(message.CommonResponse(200, batchjob_infer,
                                               '定时推理校验通过，上线成功',
                                               json.dumps(msg, default=default_dump, ensure_ascii=False)))
    if task == 'train':
        Trainer(path, reporter)
        msg = get_msg(True, '定时训练校验通过，上线成功')
        reporter.report(message.CommonResponse(200, batchjob_train,
                                               '定时训练校验通过，上线成功',
                                               json.dumps(msg, default=default_dump, ensure_ascii=False)))


def job(reporter, path, src, dst, rownumaddr, task='infer'):
    logger.info(task)
    if task != 'infer' and task != 'train':
        msg = get_batch_msg(False, int(time.time() * 1000),
                            '批处理任务任务错误，TASK环境变量必须为infer/train')
        reporter.report(message.CommonResponse(500, batchjob_infer,
                                               '批处理任务任务错误，TASK环境变量必须为infer/train',
                                               json.dumps(msg, default=default_dump, ensure_ascii=False)))

    if task == 'infer':
        infer_job(reporter, path, src, dst, rownumaddr,
                  config.DATA_SOURCE_ADDRESS)
    elif task == 'train':
        train_ratio = config.TRAIN_DATASET_RATIO
        valid_ratio = config.VALID_DATASET_RATIO
        train_job(reporter, path, src, rownumaddr, config.SOURCE_TYPE,
                  train_ratio, valid_ratio, config.DATA_SOURCE_ADDRESS)


def infer_job(reporter, path, src, dst, rownumaddr, csv_src):
    try:
        read_size = 0  # 10000
        start_time = int(time.time() * 1000)  # 1594620348908

        infer = Infer(path, reporter)
        is_read_all = False
        if read_size == 0:
            is_read_all = True
            read_size = 10000  # 防止一次性读取太多数据
        if read_size > config.DATA_SOURCE_READ_LIMIT > 0:
            read_size = config.DATA_SOURCE_READ_LIMIT

        datasets = get_dataset(src, rownumaddr)

        reader = datasets.reader(
            page_size=read_size, limit=config.DATA_SOURCE_READ_LIMIT)
        writer = get_datasource_writer(dst)

        alldata = None
        if is_read_all:
            alldata = DataSets.read_all(reader)
        else:
            for data in reader:
                alldata = data
                break
        result, err = infer.infer(alldata)
        if err is not None:
            msg = get_batch_msg(False, start_time, err)
            reporter.report(message.CommonResponse(500, batchjob_infer, '定时推理失败：{}'.format(
                err), json.dumps(msg, default=default_dump, ensure_ascii=False)))
            return

        out_result = {
            'meta': str(type(result)),
            'result': result
        }
        logger.info('批处理处理结果 {}'.format(result))
        res_data = writer.write(out_result, start_time)
        if res_data['status'] == 1:
            msg = get_batch_msg(True, start_time, '批处理输出数据成功')
            reporter.report(message.CommonResponse(200, batchjob_infer,
                                                   '批处理输出数据成功',
                                                   json.dumps(msg, default=default_dump)))
        else:
            msg = get_batch_msg(False, start_time,
                                '批处理输出数据错误 {}'.format(res_data['msg']))
            reporter.report(message.CommonResponse(500, batchjob_infer,
                                                   '批处理输出数据错误 {}'.format(
                                                       res_data['msg']),
                                                   json.dumps(msg, default=default_dump)))
        start_time = int(time.time() * 1000)
    except DataSourceReaderException as e:
        stack_info = traceback.format_exc()
        logger.error("批处理输入数据错误 {}, stack:\n{}".format(e, stack_info))
        msg = get_batch_msg(False, start_time, "批处理输入数据错误 {}".format(e))
        reporter.report(
            message.CommonResponse(500, batchjob_infer, '批处理输入数据错误', json.dumps(msg, default=default_dump, ensure_ascii=False)))
    except DataSourceWriterException as e:
        stack_info = traceback.format_exc()
        logger.error("批处理输出数据错误 {}, stack:\n{}".format(e, stack_info))
        msg = get_batch_msg(False, start_time, '"批处理输出数据错误 {}'.format(e))
        reporter.report(
            message.CommonResponse(500, batchjob_infer, '批处理输出数据错误', json.dumps(msg, default=default_dump, ensure_ascii=False)))
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error("批处理执行错误 {}, stack:\n{}".format(e, stack_info))
        msg = get_batch_msg(False, start_time, '"批处理执行错误 {}'.format(e))
        reporter.report(
            message.CommonResponse(500, batchjob_infer, '批处理执行错误', json.dumps(msg, default=default_dump, ensure_ascii=False)))


def train_job(reporter, path, src, rownumaddr, data_source_type, train_ratio, valid_ratio, csv_source_address):
    try:
        trainer = Trainer(path, reporter)
        datasets = get_dataset(src, rownumaddr)
        trainer.train(datasets)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error("训练执行错误 {}, stack:\n{}".format(e, stack_info))
        reporter.report(
            message.CommonResponse(500, "train_fail", "训练执行错误 {}, stack:\n{}".format(e, stack_info)))


class BatchService:
    def __init__(self, format, path, src, dst, rownumaddr, response_addr=None, task='infer'):
        # 按照crontab的格式给出format就可以
        self.format = format
        self.is_once = True if self.format is None or self.format == '' else False
        self.src = src
        self.dst = dst
        self.response_addr = response_addr
        self.task = task
        self.path = path
        self.reporter = RestReport(response_addr)
        self.rownumaddr = rownumaddr

        if task != 'infer' and task != 'train':
            msg = get_msg(False, '批处理任务任务错误，TASK环境变量必须为infer/train')
            self.reporter.report(message.CommonResponse(500, batchjob_infer,
                                                        '批处理任务任务错误, TASK环境变量必须为infer/train',
                                                        json.dumps(msg, default=default_dump, ensure_ascii=False)))

    def run(self):
        if self.is_once:
            logger.info("开始一次性处理任务")
            job(self.reporter, self.path, self.src, self.dst,
                self.rownumaddr, self.task)
        else:
            from intelliw.utils.crontab import Crontab
            validate_batch_job(self.reporter, self.path, self.task)
            job_list = self.__format_parse(self.format)
            crontab = Crontab(job_list)
            while True:
                try:
                    crontab.run()
                except:
                    logger.info(traceback.format_exc)
    
    def __format_parse(self, _format:str):
        format_list = []
        _format = _format.split("|")
        for idx,f in enumerate(_format):
            format_list.append(
                {
                    'name':f'job{idx}', 
                    'crontab':f.strip(), 
                    'func':job, 
                    'args':(self.reporter, self.path, self.src, self.dst,
                            self.rownumaddr, self.task)
                }
            )
        return format_list
        
