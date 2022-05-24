#!/usr/bin/env python
# coding: utf-8

import json
from .util import default_dump
from intelliw.config import config

msg_id = 0


def get_msg_id():
    global msg_id
    msg_id += 1
    return msg_id


####### return msg #########
class HealthCheckResponse:
    def __init__(self, code, typ, msg='', data=None):
        self.code = code
        self.typ = typ
        self.msg = msg
        self.data = data

    def __str__(self):
            return json.dumps({
                "extrainfo": {
                    "status": self.code,
                    "message": self.msg,
                },
                "data": self.data
            }, default=default_dump, ensure_ascii=False)


class APIResponse:
    def __init__(self, code, typ, msg='', data=None):
        self.code = code
        self.typ = typ
        self.msg = msg
        self.data = data

    def __str__(self):
        if config.API_EXTRAINFO:
            return json.dumps({
                "extrainfo": {
                    "status": self.code,
                    "message": self.msg,
                },
                "data": self.data
            }, default=default_dump, ensure_ascii=False)
        else:
            return json.dumps({"data": self.data}, default=default_dump, ensure_ascii=False)


class CommonResponse:
    def __init__(self, code, typ, msg='', data=''):
        self.code = code
        self.typ = typ
        self.msg = msg
        self.data = data

    def __str__(self):
        return json.dumps({
            "id": config.INSTANCE_ID,
            "serviceId": config.SERVICE_ID,
            "msgid": get_msg_id(),
            "token": config.TOKEN,
            "code": self.code,
            "type": self.typ,
            "message": self.msg,
            "data": self.data
        }, default=default_dump, ensure_ascii=False)


ok_infer_online_status = CommonResponse(200, "infer", "status ok")
err_import_alg_invalid_path = CommonResponse(500, "importalg", "无效算法包")
err_import_alg_mssing_algorithpy = CommonResponse(500, "importalg", "算法包必须包含: algorithm.py")
err_import_alg_mssing_algorithyaml = CommonResponse(500, "importalg", "算法包必须包含: algorithm.yaml")
err_import_alg_invalid_algorithpy_format = CommonResponse(500, "importalg", "algorithm.py 内容不符合规范")
err_import_alg_invalid_algorithyaml_format = CommonResponse(500, "importalg", "algorithm.yaml 内容不符合规范")

err_import_model_mssing_modelyaml = CommonResponse(500, "importmodel", "模型包必须包含: model.yaml")
err_import_alg_invalid_modelyaml_format = CommonResponse(500, "importmodel", "model.yaml 内容不符合规范")
err_import_model_invalid = CommonResponse(500, "importmodel", "模型参数文件无效")
err_import_model_mssing_handler = CommonResponse(500, "importhandler", "使用自定义api必须包含: apiHandler.py")

ok_import_algorithm = CommonResponse(200, "importalg", "框架导入算法成功")
ok_import_model = CommonResponse(200, "importmodel", "框架导入模型成功")
err_import_algorithm = CommonResponse(500, "importalg", "框架导入算法失败")
err_import_model = CommonResponse(500, "importmodel", "框架导入模型失败")

err_transform_support_type = \
    CommonResponse(500, "transforms",
                    "当前特征工程只支持四种类型，pre-train(训练前), post-train(训练后), pre-predict(推理前), pre-train(推理后)")

err_invalid_request = APIResponse(500, "api", "请求方法与设置不一致，未设置method，默认为POST")
err_invalid_validate_request = APIResponse(500, "validate", "无效验证请求")
err_not_initialized = CommonResponse(500, "request", "引擎初始化失败，请检查")

err_empty_infer_data = CommonResponse(500, "infer", "推理错误，处理数据为空")
err_empty_train_data = CommonResponse(500, "train_finish", "训练错误，训练数据为空")
err_empty_val_data = CommonResponse(500, "train_finish", "训练错误，验证数据为空")
err_train = CommonResponse(500, "train_finish", "训练错误，算法程序错误")
err_function_process = CommonResponse(500, "function_process", "特征值/数据处理错误")
err_dataset = CommonResponse(500, "dataSetError", '数据集存在问题')

err_missing_algorithm_mod = CommonResponse(500, "algorithm", "算法模块文件 algorithm.py 无效")
err_missing_algorithm_class = CommonResponse(500, "algorithm", "算法模块文件没有定义定义类 Algorithm ")
err_missing_train_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 train 函数")
err_missing_train_parameter = CommonResponse(500,
                                              "algorithm",
                                              "算法类 Algorithm 函数 train 参数定义不正确， 应该为 train(self, train_data)")
err_missing_score_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 score 函数")
err_missing_score_parameter = CommonResponse(500,
                                              "algorithm",
                                              "算法类 Algorithm 函数 train 参数定义不正确， 应该为 score(self, val_data)")
err_missing_report_train_info_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 report_train_info 函数")
err_missing_infer_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 infer 函数")
err_missing_infer_parameter = CommonResponse(500,
                                              "algorithm",
                                              "算法类 Algorithm 函数 infer 参数定义不正确， 应该为 infer(self, data)")
err_missing_init_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 __init__ 函数")
err_missing_init_parameter = CommonResponse(500,
                                             "algorithm",
                                             "算法类 Algorithm 函数 __init__ 参数定义不正确， 应该为 __init__(self, parameters)")
err_missing_load_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 load 函数")
err_missing_load_parameter = CommonResponse(500,
                                             "algorithm",
                                             "算法类 Algorithm 函数 load 参数定义不正确， 应该为 load(self, path)")
err_missing_save_method = CommonResponse(500, "algorithm", "算法模块文件类 Algorithm 缺少 save 函数")
err_missing_save_parameter = CommonResponse(500,
                                             "algorithm",
                                             "算法类 Algorithm 函数 save 参数定义不正确， 应该为 save(self, path)")

err_missing_router_func = CommonResponse(500, "importRouter", '初始化算法类 Algorithm 错误, 自定义api函数不存在')