#!/usr/bin/env python
# coding: utf-8

import json
import traceback
import importlib
import os
import time
import importlib.util
import sys
import copy

from intelliw.config.cfg_parser import load_config
from intelliw.datasets.datasets import DataSets
from intelliw.utils import exception
from intelliw.utils.util import prepare_algorithm_parameters, prepare_model_parameters, import_code, get_first_element
from intelliw.utils.check_algorithm_py import is_valid_algorithm
import intelliw.utils.message as message
from intelliw.core.report import RestReport
from intelliw.core.recorder import Recorder
from intelliw.utils.logger import get_logger, get_user_logger
from intelliw.config import config
from intelliw.utils.global_val import gl
from intelliw import functions


logger = get_logger()


class Const:
    # 文件
    algorithmInformation = "AlgorithmInformation"
    algorithm = "algorithm"
    algorithm_py = "algorithm.py"
    algorithm_yaml = "algorithm.yaml"
    model_yaml = "model.yaml"

    # 处理过程
    pre_predict = "pre-predict"
    post_predict = "post-predict"
    pre_train = "pre-train"
    post_train = "post-train"

    # 其他
    new_target_name = "new_target_data_unrepeatable_name"
    target_name = "targetName"
    target_col = "targetCol"
    target_code = "targetCode"


def get_model_yaml():
    return Const.model_yaml


class Pipeline:
    def __init__(self, reporter=None, perodic_interval=-1):
        self.reporter = reporter if isinstance(
            reporter, RestReport) else RestReport(reporter)
        self.alldata_transforms = None       # 自定义针对总体数据结构处理的  特征工程
        self.splitdata_transforms = None     # 自定义针对单条数据数据结构处理的  特征工程
        self.feature_transforms = None        # 内置针对总体数据结构处理的  特征工程
        self.perodic_interval = perodic_interval
        self.recorder = Recorder(self.reporter, self.perodic_interval <= 0)
        self.instance = None
        self.custom_router = []
        self.metadata = []
        gl.set("reporter", self.reporter)

    def perodic_callback_train(self):
        logger.info("定时任务： 上报状态")
        self.recorder.report()

    def perodic_callback_infer(self):
        logger.info("定时任务： 上报状态")
        self.recorder.report_infer()

    def _check_algorithm_parameters_format(self, alg):
        try:
            alg_ps = alg['parameters'] if 'parameters' in alg else None
            if alg_ps is not None:
                for _, v in enumerate(alg_ps):
                    key = v['key'] if 'key' in v else None
                    option = v['option'] if 'option' in v else None
                    if option is None:
                        return False
            return True
        except:
            return False

    def _prepare(self, path):
        sys.path.append(path)
        py_file = os.path.join(path, Const.algorithm_py)
        spec = importlib.util.spec_from_file_location(Const.algorithm, py_file)
        self.module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.module)
        return self.module

    def _initialize(self, alg_file, model_file=None):
        try:
            cfg = load_config(alg_file)
            gl.set("alg_yaml_file", alg_file)

            # 路由配置获取
            self.custom_router = cfg[Const.algorithmInformation].get(
                'router', [])

            # 算法配置获取
            alg_ps = cfg[Const.algorithmInformation][Const.algorithm].get(
                'parameters', None)
            parameters, option = prepare_algorithm_parameters(alg_ps)
            
            # model.yaml
            if model_file is not None:
                model_cfg = load_config(model_file)
                gl.set("model_yaml_file", model_file)
                self.model_cfg = model_cfg['Model']
                model_ps = self.model_cfg.get('parameters')
                
                # model and algorithm's parameters are all in this var 'parameters'
                parameters = prepare_model_parameters(
                    model_ps, parameters, option)
                
                # 从环境变量中加载PARAMETERS
                env_model_ps = os.environ.get('PARAMETERS')
                if env_model_ps:
                    env_model_ps = json.loads(env_model_ps)
                    parameters = prepare_model_parameters(
                        env_model_ps, parameters, option)

                # 算法元数据
                self.metadata = self.model_cfg.get('metadata', {})

                # 特征处理可能会修改target_col，所以需要先保存起来, 有target_name时一定会有target_col
                target_metadata_cfg = self.metadata.get("target", [])
                target_metadata = None
                if len(target_metadata_cfg) > 0:
                    target_metadata = [{"target_col": int(m[Const.target_col]), "target_name":m.get(
                        Const.target_code, m[Const.target_name])} for m in target_metadata_cfg]
                else:
                    # TODO 暂时兼容 后面删了
                    target_col = parameters.get(Const.target_col)
                    if target_col:
                        target_metadata = [{"target_col": int(
                            target_col), "target_name": parameters.get(Const.target_name)}]
                if target_metadata is not None:
                    gl.set("target_metadata", target_metadata)

                # 用户环境变量，取自metadata.userEnv
                user_env = self.metadata.get("userEnv", [])
                for ue in user_env:
                    key = str(ue.get("key", ""))
                    if key:
                        os.environ[key] = str(ue.get("value", ""))

            # 日志
            parameters["framework_log"] = get_user_logger()

            instance = self.module.Algorithm(parameters)
            logger.info("algorithm instance {}".format(instance))

            if instance is None:
                self._raise_exception(message.err_import_alg_invalid_path)

            # 检测自定义路由方法是否存在
            for router in self.custom_router:
                func = router.get('func')
                if not hasattr(instance, func):
                    self._raise_exception(message.err_missing_router_func)

            # add decorator to report functions
            if config.is_server_mode():
                from intelliw.core.al_decorator import make_decorators
                make_decorators(instance, self.reporter)

            return instance
        except Exception as e:
            self._raise_exception(message.err_import_alg_invalid_path, e)

    def _importalg_phase(self, path):
        if not os.path.isfile(os.path.join(path, Const.algorithm_py)):
            self._raise_exception(message.err_import_alg_mssing_algorithpy)
        if not os.path.isfile(os.path.join(path, Const.algorithm_yaml)):
            self._raise_exception(message.err_import_alg_mssing_algorithyaml)
        cfg = load_config(os.path.join(path, Const.algorithm_yaml))
        self.algorithm_cfg = cfg                        # SELF-DEFINE DICT
        if not self._check_algorithm_parameters_format(cfg):
            self._raise_exception(
                message.err_import_alg_invalid_algorithyaml_format)
        if self._prepare(path) is None:
            self._raise_exception(
                message.err_import_alg_invalid_algorithpy_format)

        is_valid, msg = is_valid_algorithm(self.module)
        if not is_valid:
            self._raise_exception(msg)

    def importalg(self, path):
        """
        导入算法
        :param path: 算法包所在路径
        :return: None
        :raises PipelineException: 框架导入算法失败原因
        """
        try:
            self._importalg_phase(path)
            self._initialize(os.path.join(path, Const.algorithm_yaml))
        except Exception as e:
            self._raise_exception(message.err_import_algorithm, e)
        self.reporter.report(message.ok_import_algorithm)

    def importmodel(self, path, load_model=True):
        """
        导入模型
        :param path: 算法包所在路径
        :param load_model: 是否要导入模型，即是否调用 Algorithm 的 load 方法
        :return: None
        :raises PipelineException: 框架导入模型失败原因
        """
        if not os.path.isfile(os.path.join(path, Const.model_yaml)):
            logger.error(
                "未找到 model.yaml, path: {}, file_name: {}".format(path, Const.model_yaml))
            self._raise_exception(message.err_import_model_mssing_modelyaml)
        try:
            self._importalg_phase(path)
        except Exception as e:
            self._raise_exception(message.err_import_model, e)
        self.instance = self._initialize(os.path.join(
            path, Const.algorithm_yaml), os.path.join(path, Const.model_yaml))
        try:
            trans_cfg = self.model_cfg.get('transforms', None)
            self.splitdata_transforms, self.alldata_transforms, self.feature_transforms = self.prepare_transforms(
                trans_cfg)
            gl.set('feature_process', self.feature_transforms)
            if load_model:
                model_file = os.path.join(path, self.model_cfg['location'])
                self.instance.load(model_file)
        except Exception as e:
            self._raise_exception(message.err_import_model, e)
        self.reporter.report(message.ok_import_model)

    def _vaild_transforms_cfg(self, stage, is_splte):
        transforms = self.splitdata_transforms if is_splte else self.alldata_transforms
        if transforms is not None:
            transforms = transforms.get(stage)
            if transforms:
                return transforms
        return None

    def _transform_helper(self, stage, data, is_splte):
        transforms = self._vaild_transforms_cfg(stage, is_splte)
        if transforms is not None:
            return self.transform_call_chains(transforms, data)
        return data

    def _transform_function(self, stage, is_splte):
        if self._vaild_transforms_cfg(stage, is_splte) is None:
            return None

        def _transform(data):
            return self._transform_helper(stage, data, is_splte)
        return _transform

    def _valid_feature_transforms(self, stage):
        if self.feature_transforms is not None:
            params = self.feature_transforms.get(stage)
            if params:
                return params
        return None

    def _feature_helper(self, stage, data, _type=None):
        params = self._valid_feature_transforms(stage)
        if params is not None:
            return functions.feature_process(data, params, stage, _type)
        return data

    def _feature_process(self, stage):
        if self._valid_feature_transforms(stage) is None:
            return None

        def _process(data, _type=None):
            return self._feature_helper(stage, data, _type)
        return _process

    def train(self, datasets: DataSets):
        if datasets is None:
            self._raise_exception(message.err_empty_train_data)

        # 特征值处理
        try:
            train_reader = datasets.train_reader(
                self._transform_function(Const.pre_train, True), 
                self._transform_function(Const.pre_train, False), 
                self._feature_process(Const.pre_train)
            )
            valid_reader = datasets.validation_reader(
                self._transform_function(Const.pre_train, True), 
                self._transform_function(Const.pre_train, False), 
                self._feature_process(Const.pre_train)
            )
        except Exception as e:
            self._raise_exception(message.err_function_process, e)
            
        # 开始训练
        try:
            logger.info("data process success, start train mode")
            train_func = getattr(self.instance, "train")
            if "kwargs" in train_func.__code__.co_varnames:
                feature_process_cfg = gl.pop("feature_process")
                if feature_process_cfg is not None:
                    feature_process_cfg = {Const.pre_train: feature_process_cfg.get(
                        Const.pre_train), Const.post_train: feature_process_cfg.get(Const.post_train)}
                kwargs = {
                    "final_target_col": gl.pop("final_target_col"),
                    "target_cols": gl.pop("target_cols"),
                    "category_cols": gl.pop("category_cols"),
                    "column_meta": gl.pop("column_meta") if gl.get("column_meta") is not None else DataSets.get_col_list(train_reader),
                    "column_relation_df": gl.pop("column_relation_df"),
                    "feature_process_cfg": feature_process_cfg,
                }
                train_func(train_reader, valid_reader, **kwargs)
            else:
                train_func(train_reader, valid_reader)
            self.reporter.report(message.CommonResponse(
                200, 'train_finish', '', ''))
        except exception.DatasetException as de:
            self._raise_exception(message.err_dataset, de,
                                  is_farmeworl_error=False)
        except Exception as e:
            self._raise_exception(message.err_train, e,
                                  is_farmeworl_error=False)

    def infer(self, data, request, func='infer', need_featrue=True):
        starttime = int(time.time() * 1000)
        try:
            logger.debug("receiving predict data {}".format(data))
            # 前处理
            if need_featrue:
                data = self._transform_helper(Const.pre_predict, data, False)
                data = self._feature_helper(Const.pre_predict, data, "infer")
            
            # 推理
            self.instance.request = request
            infer_func = getattr(self.instance, func)
            if infer_func.__code__.co_argcount > 1:  # 获取函数参数数量
                result = infer_func(data)
            else:
                result = infer_func()
            
            # 后处理
            if need_featrue:
                result = self._feature_helper(Const.post_predict, result, "infer")
                result = self._transform_helper(Const.post_predict, result, False)
            logger.debug("预测输出 {}".format(result))
            self.recorder.record_infer_status(
                '', True, starttime, int(time.time() * 1000))
            return result, None
        except Exception as e:
            stack_info = traceback.format_exc()
            logger.error("推理错误 {}, stack:\n{}".format(e, stack_info))
            self.recorder.record_infer_status('', False, starttime,
                                              int(time.time() * 1000), '{}'.format(e))
            return None, str("推理错误 {}".format(e))

    def transform_call_wrapper(self, src, func, params):
        if type(func) is type:
            return func().__call__(src, params)
        else:
            return func(src, params)

    def transform_call_chains(self, funcs, src):
        try:
            for _, item in enumerate(funcs):
                (name, func, params) = item
                fp = gl.get('feature_process')
                # 如果有特征工程前处理，就需要忽略select_columns， 要不会导致列下标错误
                if func == functions.select_columns and fp is not None and fp.get(Const.pre_train) is not None:
                    continue
                src = self.transform_call_wrapper(src, func, params)
            return src
        except Exception as e:
            msg = message.CommonResponse(500, "transforms", "特征工程函数 {} 出错".format(name))
            self._raise_exception(msg, e)

    def _get_func_by_name(self, name):
        """
        根据 name 加载函数

        加载顺序:
        1. 尝试在算法项目中加载
        2. 尝试在内置的特征处理中查找
        3. 尝试在当前 module 中加载

        :param name: 待加载的函数名称
        :return: 函数
        :raise: RuntimeError 加载失败原因
        """
        # 尝试在算法项目中加载
        mod = self.module
        if hasattr(mod, name):
            return getattr(mod, name)

        # 尝试在内置的特征处理中查找
        if hasattr(functions, name):
            return getattr(functions, name)

        # 尝试在当前 module 中加载
        mod = sys.modules[__name__]
        if hasattr(mod, name):
            return getattr(mod, name)

        raise RuntimeError('函数无效: [{}]'.format(name))

    def prepare_transforms(self, cfgs):
        def init_dict(f): return dict() if f is None else f
        def init_list(f): return list() if f is None else f
        # 没用到就不初始化，减少后面的判断
        split_transforms, alldate_transforms, features = None, None, None
        if cfgs:
            for v in cfgs:
                typ, functions_cfg = v.get('type'), v.get('functions')
                if typ is not None and functions_cfg is not None:
                    for item in functions_cfg:
                        key, parameters = item.get(
                            'key'), item.get('parameters')
                        params, _ = prepare_algorithm_parameters(parameters)
                        if key == functions.Const.feature_process:
                            features = init_dict(features)
                            features[typ] = init_list(features.get(typ))
                            features[typ] = json.loads(params.get(
                                functions.Const.feature_process_param, 'null'))
                        else:
                            body = item.get('body')
                            func = self._get_func_by_name(
                                key) if body is None else get_first_element(import_code(body, None))
                            if func is not None:
                                can_split = key in functions.Const.split_function_list or item.get(
                                    'canSplit', False)
                                logger.info(
                                    "特征函数 {}, 是否可以进行分片处理 {}".format(key, can_split))
                                if can_split == True:
                                    split_transforms = init_dict(
                                        split_transforms)
                                    split_transforms[typ] = init_list(
                                        split_transforms.get(typ))
                                    split_transforms[typ].append(
                                        (key, func, params))
                                else:
                                    alldate_transforms = init_dict(
                                        alldate_transforms)
                                    alldate_transforms[typ] = init_list(
                                        alldate_transforms.get(typ))
                                    alldate_transforms[typ].append(
                                        (key, func, params))
                            else:
                                logger.info(
                                    "找不到函数 {}".format(key))
        return split_transforms, alldate_transforms, features

    def validate_transforms(self, cfgs, data):
        """
        验证特征工程函数， 用于用户校验函数正确性和结果，服务于validateService
        """
        transforms = []
        if cfgs is not None:
            for _, v in enumerate(cfgs):
                functions = v['functions'] if 'functions' in v else None
                if functions is not None:
                    for k, item in enumerate(functions):
                        desc = item['desc'] if 'desc' in item else None
                        key = item['key'] if 'key' in item else None
                        body = item['body'] if 'body' in item else None
                        parameters = item['parameters'] if 'parameters' in item else None
                        if body is not None:
                            nmod = import_code(body, None)
                            func = get_first_element(nmod)
                        else:
                            func = self._get_func_by_name(key)
                        params, _ = prepare_algorithm_parameters(parameters)
                        if func is not None:
                            logger.info("特征函数 {}".format(key))
                            transforms.append((key, func, params))
                        else:
                            logger.info("找不到函数 {}".format(key))

        return self.transform_call_chains(transforms, data)

    def _raise_exception(self, msg: message.CommonResponse, e: Exception = None, is_farmeworl_error=True):
        if is_farmeworl_error:
            raise_logger = logger
        else:
            raise_logger = get_user_logger()

        err_msg = "[{}]".format(msg.msg)
        # 用于传递错误给prepare_env.sh
        err_stack = ""
        if isinstance(e, exception.DatasetException):
            err_stack = str(e)
        elif e:
            err_stack = traceback.format_exc()
        err_msg += err_stack
        os.environ["ERR_MASSAGE"] = err_msg

        # e 为空，打印、上报、抛异常
        if e is None:
            raise_logger.error(msg.msg)
            self.reporter.report(msg)
            raise exception.PipelineException(msg.msg)

        # PipelineException 说明已经上报过了，打印过日志了，直接上抛
        if isinstance(e, exception.PipelineException):
            raise e

        # 其他异常打印日志后上报错误
        raise_logger.error(msg.msg + ' %s', e, exc_info=True)
        msg.msg = err_msg
        self.reporter.report(msg)

        if isinstance(e, exception.DatasetException):
            sys.exit()

        raise exception.PipelineException(msg.msg) from e
