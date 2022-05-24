#!/usr/bin/env python
# coding: utf-8

import inspect
import json
import time
import errno
import shutil
import os
import zipfile
import traceback
from functools import wraps
from intelliw.config.cfg_parser import load_config
import intelliw.utils.message as message
from intelliw.utils.util import default_dump, generate_random_str
from intelliw.utils.storage_service import StorageService
from intelliw.utils.logger import get_logger
from intelliw.config import config

logger = get_logger()


def zipdir(mpath):
    outpath = '/tmp/model.zip'
    with zipfile.ZipFile(outpath, 'w', zipfile.ZIP_DEFLATED) as zipf:
        if os.path.isdir(mpath):
            for root, dirs, files in os.walk(mpath):
                relative_path = root.replace(mpath, "")
                for file in files:
                    logger.info("压缩文件 {}".format(os.path.join(root, file)))
                    zipf.write(os.path.join(root, file),os.path.join(relative_path, file))
        elif os.path.isfile(mpath):
            zipf.write(mpath, os.path.basename(mpath))
    return outpath


class TrainInfo:
    def __init__(self, loss, lr, iter, batchsize):
        self.loss = loss
        self.lr = lr
        self.iter = iter
        self.batchsize = batchsize

    def __str__(self):
        return json.dumps({
            "loss": self.loss,
            "lr": self.lr,
            "iter": self.iter,
            "batchsize": self.batchsize,
            "timestamp": int(time.time() * 1000)
        }, default=default_dump)


def decorator_report_train_info(function, reporter=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if reporter is not None:
            info = TrainInfo(*args)
            reporter.report(message.CommonResponse(200, 'report_train_info', '', str(info)))
        return function(*args, **kwargs)
    return wrapper


def decorator_report_val_info(function, reporter=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        if reporter is not None:
            val = {}

            # process args
            varnames = function.__code__.co_varnames
            offset = 0
            for i in range(len(varnames)):
                if varnames[i] == 'self' or varnames[i] == 'args' or varnames[i] == 'kwargs':
                    offset = offset - 1
                    continue
                if i + offset < len(args):
                    val[varnames[i]] = args[i + offset]
                else:
                    val[varnames[i]] = None

            # process kwargs
            for k, v in kwargs.items():
                val[k] = v

            data = {
                "modelInstanceId": config.INSTANCE_ID,
                "tenantId": config.TENANT_ID,
                "valuationResult": val
            }
            reporter.report(message.CommonResponse(200, 'report_val_info', '', json.dumps(data, default=default_dump, ensure_ascii=False)))
        return function(*args, **kwargs)
    return wrapper     


# decorator_save 存储模型文件到云存储
def decorator_save(function, reporter=None):
    @wraps(function)
    def wrapper(*args, **kwargs):
        hpath = os.path.join('/tmp', generate_random_str(16))
        os.makedirs(hpath)
        mpath = os.path.join(hpath, args[0])
        abs_path = os.path.abspath(mpath)
        if mpath.endswith('/') or mpath.endswith('\\'):
            # 如传入的是目录，则拼接上路径分隔符，以保证获取 dir_path 时包括末级路径
            abs_path = abs_path + os.sep
        dir_path = os.path.dirname(abs_path)
        if not os.path.exists(dir_path):
            logger.info("目录不存在， 自动创建 {}".format(dir_path))
            try:
                os.makedirs(dir_path)
            except OSError as e:
                if e.errno == errno.EEXIST and os.path.isdir(dir_path):
                    pass
                else:
                    logger.error("保存模型错误:  创建目录失败")
                    reporter.report(str(message.CommonResponse(500, "train_save",
                                                               "保存模型错误:  创建目录失败 {}".format(dir_path))))
        result = function(mpath)
        if reporter is not None:
            try:
                outpath = zipdir(os.path.abspath(mpath))
                curkey = os.path.join(
                    config.STORAGE_SERVICE_PATH, generate_random_str(32))
                env_val = os.environ.get("FILE_UP_TYPE").upper()
                if env_val == "MINIO":
                    client_type = "Minio"
                elif env_val == "ALIOSS":
                    client_type = "AliOss"
                elif env_val == "HWOBS":
                    client_type = "HWObs"
                else:
                    raise TypeError(f"FILE_UP_TYPE err: {env_val}")
                uploader = StorageService(curkey, client_type, "upload")
                logger.info(f"上传模型文件到{client_type}")
                try:
                    uploader.upload(outpath)
                    logger.info(f"上传模型文件到{client_type}成功： {curkey}")
                    reporter.report(message.CommonResponse(
                        200, 'train_save', 'success', [curkey]))
                except:
                    err_info = traceback.format_exc()
                    logger.info(f"上传模型文件到{client_type}失败: {err_info}")
                    reporter.report(str(message.CommonResponse(
                        500, "train_save", f"保存模型错误 {err_info}")))

                shutil.rmtree(hpath)
                os.remove(outpath)
            except Exception as e:
                stack_info = traceback.format_exc()
                reporter.report(str(message.CommonResponse(500, "train_save",
                                                           "保存模型错误 {}, stack: \n {}".format(e, stack_info))))
        else:
            logger.info("保存模型错误:  reporter is  None")
        return result
    return wrapper



def make_decorators(instance, reporter=None):
    # report_train_info
    if (hasattr(instance, 'report_train_info')) and inspect.ismethod(instance.report_train_info):
        instance.report_train_info = decorator_report_train_info(
            instance.report_train_info, reporter)

    # report_val_info
    if (hasattr(instance, 'report_val_info')) and inspect.ismethod(instance.report_val_info):
        instance.report_val_info = decorator_report_val_info(
            instance.report_val_info, reporter)

    # save model
    if (hasattr(instance, 'save')) and inspect.ismethod(instance.save):
        instance.save = decorator_save(instance.save, reporter)
