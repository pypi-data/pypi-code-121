import os
import traceback
import requests
from intelliw.datasets.datasets import get_dataset
from intelliw.interface.apijob import ApiService
from intelliw.core.infer import Infer
from intelliw.core.trainer import Trainer
from intelliw.utils.logger import get_logger
from intelliw.utils.gen_model_cfg import generate_model_config_from_algorithm_config as __generate
from intelliw.config import config as iwconfig
from intelliw import set_dataset_config
report_addr = None
logger = get_logger()



#########################################################
#                请按照需求填写以下配置                     #
#########################################################
# (必须)设置算法文件位置（algorithms.py根目录）
PACKAGE_PATH = None

algorithm_yaml_path = os.path.join(PACKAGE_PATH, 'algorithm.yaml')
model_yaml_path = os.path.join(PACKAGE_PATH, 'model.yaml')
iwconfig.RUNNING_MODE = 'SCAFFOLDING'


# 训练测试(通过算法框架调用train)
def debug_train():
    '''(debug_train时必填)
    设置训练测试数据
    example: 
        DATASET_ID = "asdasdasdasdas"   数据集id,获取途径 AI工作坊数据集管理中获取id, 不使用传入None
        TRAIN_CSV_PATH = "/home/xxx/data.csv"   本地训练csv, 如果写了DATASET_ID, 优先DATASET_ID
        TRAIN_DATASET_RATIO = 0.7 数据集比例,验证集为1-TRAIN_DATASET_RATIO, 值在0-1之间
        iwconfig.DATA_SPLIT_MODE = 0    数据集划分模式, 0 顺序划分,1 随机划分, 2 根据特征列进行划分(需要在algorithm.yaml的超参中增加targetCol,来指明特征列下标)
    '''
    DATASET_ID = None
    TRAIN_CSV_PATH = None
    TRAIN_DATASET_RATIO = 0.7
    set_dataset_config(DATASET_ID, TRAIN_DATASET_RATIO, TRAIN_CSV_PATH)
    iwconfig.DATA_SPLIT_MODE = 1
    
    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        trainer = Trainer(PACKAGE_PATH)
        train_data = get_dataset(iwconfig.INPUT_ADDR, iwconfig.INPUT_GETROW_ADDR)
        trainer.train(train_data)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))


# 推理测试
def debug_infer():
    '''(debug_infer时必填)
    设置推理训练数据
    example: INFER_DATA = {"data":[1,2,3]}
    '''
    INFER_DATA = None
    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        infer = Infer(PACKAGE_PATH)
        result = infer.infer(INFER_DATA)
        print(result)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))


# 多api测试
def debug_router():
    '''(debug_router时必填)
    设置多api
    example:
        INFER_DATA = {"data":base64}
        ROUTER_FUNC = api_test
    '''
    INFER_DATA = None
    ROUTER_FUNC = None

    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        infer = Infer(PACKAGE_PATH)
        instance = infer.pipeline.instance
        result = getattr(instance, ROUTER_FUNC)(INFER_DATA)
        print(result)
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute pipeline and stack:\n{}".format(str(stack_info)))


# http服务测试
def debug_infer_http_server():
    # (debug_infer_http_server时必填)设置http服务测试
    SERVER_PORT = 8080

    try:
        __generate(algorithm_yaml_path, model_yaml_path)
        apiservice = ApiService(SERVER_PORT, PACKAGE_PATH, report_addr)
        apiservice.run()
    except Exception as e:
        stack_info = traceback.format_exc()
        logger.error(
            "fail to execute apiService and stack:\n{}".format(str(stack_info)))


# http接口测试
def debug_server_available():
    '''(debug_server_available时必填)
    http接口测试
    example：
        URL = "http://xxx.xxx.xxx/predict"
        METHOD = "get/post"
        INFER_DATA = {"data":base64}
    '''
    URL = "https://127.0.0.1:8888/predict"
    METHOD = "post"
    INFER_DATA = None

    resp = requests.request(METHOD, URL, json=INFER_DATA, timeout=60)
    if resp.status_code != requests.codes.ok:
        resp.raise_for_status()
    print(resp.content)


if __name__ == '__main__':
    if PACKAGE_PATH == None:
        raise FileNotFoundError("请在debug_contorler.py中设置PACKAGE_PATH")
    debug_train()
    # debug_infer()
    # debug_router()
    # debug_infer_http_server()
    # debug_server_available()
