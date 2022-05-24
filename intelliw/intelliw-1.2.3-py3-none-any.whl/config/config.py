import json
import os
import sys
import inspect
from unittest import result

# 运行模式 SCAFFOLDING 脚手架，SERVER 服务端
RUNNING_MODE = 'SERVER'

# basic
TENANT_ID = 'rjtfwo7u'
# 实例 id，代表当前运行实例
INSTANCE_ID = ''
# 推理任务 id
INFER_ID = ''
# 任务 id，推理任务时与 INFER_ID 相同
SERVICE_ID = ''
# 是否专属化
IS_SPECIALIZATION = 0

# 数据集相关
SOURCE_TYPE = 3  # 输入数据源类型，0 空，1 远程 csv，2 智能分析，3 本地 csv， 4 图片数据源， 5 数据工场
INPUT_ADDR = ''
INPUT_GETROW_ADDR = ''
INPUT_MODEL_ID = ''
INPUT_DATA_SOURCE_ID = ''
INPUT_DATA_SOURCE_TRAIN_TYPE = 3

DATASET_BY_ID_ADDRESS = "" # 通过url可以获取数据集所需的所有环境信息

OUTPUT_DATA_SOURCE_ID = ''
OUTPUT_SOURCE_TYPE = 0  # 输出数据源类型，0 空，2 智能分析, 5 数据工场

CSV_PATH = ''     # 本地 csv 数据源路径
DATA_SOURCE_ADDRESS = ''   # 远程 csv 数据源地址

DATA_SOURCE_READ_SIZE = 1000
DATA_SOURCE_READ_LIMIT = sys.maxsize

TRAIN_DATASET_RATIO = 0.8   # 训练集比例
VALID_DATASET_RATIO = 0.2   # 验证集比例
TEST_DATASET_RATIO = 0      # 测试集比例
DATA_SPLIT_MODE = 1         # 数据集划分模式, 0 顺序划分，1 全局随机划分，2 根据目标列随机划分，3 局部随机划分


# cv数据存储文件名
CV_IMG_FILEPATH = "tmp_local_cv_image_data/"
CV_IMG_TRAIN_FILEPATH = os.path.join(CV_IMG_FILEPATH, "train/")
CV_IMG_VAL_FILEPATH = os.path.join(CV_IMG_FILEPATH, "val/")
CV_IMG_VAL_FILEPATH = os.path.join(CV_IMG_FILEPATH, "test/")
CV_IMG_ANNOTATION_FILEPATH = os.path.join(CV_IMG_FILEPATH, "annotations/")


# 推理服务
TOKEN = ''             # API 响应 token
API_EXTRAINFO = True   # API 响应包含 extra info
PERODIC_INTERVAL = -1  # Infer上报间隔，单位秒，-1 永不上报

# 云存储相关
STORAGE_SERVICE_PATH = ''
STORAGE_SERVICE_URL = ''
FILE_UP_TYPE = ""   # 对应的类型 AliOss/Minio

# AuthSDK
ACCESS_KEY = ''
ACCESS_SECRET = ''


def is_server_mode():
    return 'SERVER' == RUNNING_MODE


def update_by_env():
    module = sys.modules[__name__]
    for k, v in module.__dict__.items():
        if k.startswith('__') or inspect.isfunction(v) or inspect.ismodule(v):
            continue
        env_val = os.environ.get(k)
        if env_val is None:
            env_val = os.environ.get(k.upper())

        if env_val is not None:
            if env_val != '':
                setattr(module, k, type(getattr(module, k))(env_val))
            elif env_val == '' and isinstance(getattr(module, k), str):
                setattr(module, k, env_val)


def set_dataset_config(dataset_id: str = None, dataset_ratio: float = 0.7, loacl_csv: str = None):
    """通过ai工作坊接口设置数据集所需的环境变量

    Args:
        dataset_id (str): 数据集id, 从ai工作坊页面上获取

    所需环境变量:
        SOURCE_TYPE = 3
        INPUT_MODEL_ID = ''
        INPUT_DATA_SOURCE_ID = ''
        INPUT_DATA_SOURCE_TRAIN_TYPE = 2
        DATA_SOURCE_ADDRESS = ''

        if SOURCE_TYPE = 1
            NEED: DATA_SOURCE_ADDRESS
        if SOURCE_TYPE = 2
            NEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_MODEL_ID
        if SOURCE_TYPE = 4
            NEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_DATA_SOURCE_ID, INPUT_DATA_SOURCE_TRAIN_TYPE
        if SOURCE_TYPE = 5
            BEED: INPUT_ADDR, INPUT_GETROW_ADDR, INPUT_DATA_SOURCE_ID
    """

    assert 0.0 <= dataset_ratio <= 1.0
    if not dataset_id  and not os.path.exists(loacl_csv):
        raise Exception("数据集错误,请通过--csv设置本地csv文件, 或者--dataset设置在线数据集")

    module = sys.modules[__name__]
    setattr(module, "TRAIN_DATASET_RATIO", dataset_ratio)
    setattr(module, "VALID_DATASET_RATIO", 1-dataset_ratio)
    if not dataset_id:
        setattr(module, "SOURCE_TYPE", 3)
        setattr(module, "CSV_PATH", loacl_csv)
    else:
        from intelliw.utils import iuap_request
        DATASET_URL = os.environ.get('DATASET_BY_ID_ADDRESS')
        resp = iuap_request.get(DATASET_URL, params={"dataSetId":dataset_id})
        resp.raise_for_status()
        body = json.loads(resp.body)
        if body['status'] == 0:
            raise Exception(body['msg'])
        result = body['data']
        source = result["SOURCE_TYPE"]
        setattr(module, "SOURCE_TYPE", source)
        if source == 1:
            setattr(module, "DATA_SOURCE_ADDRESS", result["DATA_SOURCE_ADDRESS"])
        else:
            setattr(module, "INPUT_ADDR", result["INPUT_ADDR"])
            setattr(module, "INPUT_GETROW_ADDR", result["INPUT_GETROW_ADDR"])
            if source == 2:
                setattr(module, "INPUT_MODEL_ID", result["INPUT_MODEL_ID"])
            elif source == 4:
                setattr(module, "INPUT_DATA_SOURCE_ID", result["INPUT_DATA_SOURCE_ID"])
            elif source == 5:
                setattr(module, "INPUT_DATA_SOURCE_ID", result["INPUT_DATA_SOURCE_ID"])
