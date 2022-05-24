#!/usr/bin/env python
# coding: utf-8
'''
Author: hexu
Date: 2021-10-25 15:20:34
LastEditTime: 2022-04-20 14:59:01
LastEditors: Hexu
Description: 线上调用的入口文件
FilePath: /iw-algo-fx/intelliw/interface/controller.py
'''
import os
import argparse
import traceback

from intelliw.utils.logger import get_logger
logger = get_logger()


from intelliw.core.pipeline import get_model_yaml
from intelliw.core.pipeline import Pipeline
from intelliw.interface.apijob import ApiService
from intelliw.interface.goinferjob import InferService
from intelliw.interface.batchjob import BatchService
from intelliw.interface.validatejob import ValidateService

from intelliw.config.cfg_parser import load_config
from intelliw.config import config




class FrameworkArgs:
    def __init__(self, args=None):
        self.path = "" if args is None else args.path
        self.method = "importalg" if args is None else args.method
        self.name = "predict" if args is None else args.name
        self.input = "" if args is None else args.input
        self.output = "" if args is None else args.output
        self.format = "" if args is None else args.format
        self.task = "infer" if args is None else args.task
        self.port = 8888 if args is None else args.port
        self.response = None if args is None else args.response
        self.rownumaddr = None if args is None else args.rownumaddr


def __parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-p", "--path", default="",
                        type=str, help="package path")
    parser.add_argument("-m", "--method", default="importalg",
                        type=str, help="method")
    parser.add_argument("-n", "--name", default="predict",
                        type=str, help="name")
    parser.add_argument("-i", "--input", default="", type=str, help="input")
    parser.add_argument("-o", "--output", default="", type=str, help="output")
    parser.add_argument("-f", "--format", default="",
                        type=str, help="batch format")
    parser.add_argument("-t", "--task", default="infer",
                        type=str, help="task type: infer/train")
    parser.add_argument("--port", default=8888, type=int, help="port")
    parser.add_argument("-r", "--response",
                        default=None, type=str, help="response addr, which can be used to report status")
    parser.add_argument("-w", "--rownumaddr", default=None,
                        type=str, help="number of rows")

    return parser.parse_args()


def is_high_performance(module_file_path):
    if not os.path.isfile(module_file_path):
        logger.error("未找到 model.yaml, path: {}".format(module_file_path))
        raise Exception("未找到 model.yaml")
    cfg = load_config(module_file_path)
    model_cfg = cfg['Model']
    if 'enableHighPerformanceInfer' in model_cfg and model_cfg['enableHighPerformanceInfer'] is True:
        return True
    return False


def main(args):
    try:
        if args.method == "importalg":
            pl = Pipeline(args.response)
            pl.importalg(args.path)
        elif args.method == "importmodel":
            is_high = is_high_performance(
                os.path.join(args.path, get_model_yaml()))
            if is_high:
                infer = InferService(args.name, args.port,
                                     args.path, args.response)
                infer.check()
            else:
                pl = Pipeline(args.response)
                pl.importmodel(args.path)
        elif args.method == "apiservice":
            is_high = is_high_performance(
                os.path.join(args.path, get_model_yaml()))
            if is_high:
                infer = InferService(args.name, args.port,
                                     args.path, args.response)
                infer.run()
            else:
                apiservice = ApiService(args.port, args.path, args.response)
                apiservice.run()
        elif args.method == "batchservice":
            logger.warn("rownumaddr:{}, input:{}".format(
                args.rownumaddr, args.input))
            batchservice = BatchService(
                args.format, args.path, args.input, args.output, args.rownumaddr, args.response, args.task)
            batchservice.run()
        elif args.method == "validateservice":
            validateservice = ValidateService(
                args.name, args.port, args.path, args.response)
            validateservice.run()
        exit(0)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error("fail to execute and stack:\n{}".format(str(stack_info)))
        exit(1)


def run():
    framework_args = FrameworkArgs(__parse_args())
    config.update_by_env()
    main(framework_args)


if __name__ == '__main__':
    framework_args = FrameworkArgs(__parse_args())
    config.update_by_env()
    main(framework_args)
