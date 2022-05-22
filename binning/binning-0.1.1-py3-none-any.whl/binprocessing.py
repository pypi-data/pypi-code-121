from typing import Any, Callable, Dict

import pandas as pd

from .chimerge_bin import ChimergeBin
from .constants import N_CPU
from .custom_bin import CustomBin
from .distance_bin import DistanceBin
from .enumerate_bin import EnumerateBin
from .enums import BinType
from .frequency_bin import FrequencyBin
from .log_utils import get_fmpc_logger
from .tool import Tool
from .wrap_utils import exec_except, exec_time

logger = get_fmpc_logger(__name__)


class BinProcessing:
    """分箱逻辑入口

    Args:
        bin_type (str): 分箱类型
        features (Dict[str,int]): 特征集
        df (pd.DataFrame): 分箱数据源
        parallel (bool): 是否并行
        log (Callable): 日志函数

        bins_merge (bool): 是否合并箱

    Local:
        params (Dict[str, Any]): 处理器参数
        handler (class): 处理器
        tool (Any): 工具类
    """

    def __init__(self,
                 bin_type: str,
                 features: Dict[str, int],
                 df: pd.DataFrame,
                 parallel: bool,
                 log: Callable,
                 **kwargs):
        self.bin_type = bin_type
        self.features = features.copy()
        self.df = df.copy()
        self.parallel = parallel
        self.log = log

        self.bins_merge = True

        self.params = {}
        self.handler = None

        self.tool = Tool()
        self.preprocess(kwargs)

    @exec_time
    @exec_except
    def preprocess(self, kwargs):
        """preprocess"""
        self._check(kwargs)
        self._validate(kwargs)
        self._assemble_params(kwargs)
        self._assemble_handler()

    def _check(self, kwargs):
        """check"""
        if not self.bin_type:
            raise ValueError(f"分箱方式bin_type为空，请检查")

        if not self.features:
            raise ValueError(f"特征集features为空，请检查")

        if self.df.empty:
            raise ValueError(f"分箱数据源df为空，请检查")

        if not isinstance(self.parallel, bool):
            raise TypeError(f"并行参数为bool类型，请检查")

        if not isinstance(self.log, Callable):
            raise TypeError(f"日志函数为Callable类型，请检查")

        if not kwargs:
            raise ValueError(f"参数不全，请检查")

    def _validate(self, kwargs):
        """validate"""
        if kwargs.get("bins_merge") and not isinstance(kwargs.get("bins_merge"), bool):
            raise ValueError(f"参数bins_merge是bool类型，请检查")

        if kwargs.get("role") and kwargs.get("role") != "GUEST" and kwargs.get("role") != "HOST":
            raise ValueError(f"参数role为GUEST或者HOST，请检查")

        if kwargs.get("bins_merge") and kwargs.get("role") == "HOST":
            if not kwargs.get("guest_nid"):
                raise ValueError(f"参数guest_nid为空，请检查")
            if not kwargs.get("data_transfer"):
                raise ValueError(f"参数data_transfer为空，请检查")
            if not kwargs.get("send_features_dict_event_name"):
                raise ValueError(f"参数send_features_dict_event_name为空，请检查")
            if not kwargs.get("get_bins_dict_event_name"):
                raise ValueError(f"参数get_bins_dict_event_name为空，请检查")

        if set(self.features.keys()) > set(self.df.columns):
            raise ValueError(f"特征列{self.features.keys()}不完全在数据源中{self.df.columns}，请检查")

    def _get_parallel_info(self):
        """parallel info"""
        if self.parallel:
            features_ = list(self.features.keys())
            n_features = len(features_)
            n_cpu = N_CPU
            n_split, n_parallel = self.tool.get_n_split_n_parallel(n_cpu, n_features)
            features_lst = self.tool.data_slice(features_, n_split)

            logger.info(f'==>> 最大并行CPU数:{n_cpu}，实际并行CPU数:{n_parallel}')
            logger.info(f'==>> 数据总特征数:{n_features}，单个并行特征数:{n_split}')
            logger.info(f'==>> 拆分特征:{features_lst}')

            return {"parallel": self.parallel,
                    "n_parallel": n_parallel,
                    "features_lst": features_lst}
        else:
            return {"parallel": self.parallel}

    def _assemble_params(self, kwargs):
        """assemble params"""
        if not kwargs.get("label"):
            kwargs["label"] = "y"
            self.df["y"] = 1
        if kwargs.get("bins_merge") is not None:
            self.bins_merge = kwargs.get("bins_merge")
        if not kwargs.get("role"):
            kwargs["role"] = "GUEST"

        kwargs["features"] = self.features
        kwargs["df"] = self.df
        kwargs["parallel_info"] = self._get_parallel_info()
        self.params = kwargs

    def _assemble_handler(self):
        """assembling handler"""
        if self.bin_type == BinType.DISTANCE_BIN.name:
            self.handler = DistanceBin(**self.params)
        elif self.bin_type == BinType.FREQUENCY_BIN.name:
            self.handler = FrequencyBin(**self.params)
        elif self.bin_type == BinType.ENUMERATE_BIN.name:
            self.handler = EnumerateBin(**self.params)
        elif self.bin_type == BinType.CUSTOM_BIN.name:
            self.handler = CustomBin(**self.params)
        elif self.bin_type == BinType.CHIMERGE_BIN.name:
            self.handler = ChimergeBin(**self.params)
        else:
            raise TypeError(f"暂不支持此分箱{self.bin_type}")

    def get_bins_dict(self) -> Dict[str, Any]:
        """get bins dict

        Returns:
            Dict[str, Any]: {"feature": List[Any], ...}
        """
        role = self.params.get("role")
        logger.info(f"{LOG_PREFIX}生成特征字典")
        if self.bin_type == BinType.CHIMERGE_BIN.name and role == "HOST":
            features_dict = self.handler.bin_process_host(log=self.log)
        else:
            features_dict = self.handler.bin_process(log=self.log)

        logger.info(f"{LOG_PREFIX}分箱合并")
        if not self.bins_merge:
            logger.info(f"{LOG_PREFIX}不进行分箱合并，生成分箱区间")
            bins_dict = self.tool.convert_bins_dict(self.features, features_dict)
        else:
            if role == "GUEST":
                logger.info(f"{LOG_PREFIX}{role}合并分箱，生成分箱区间")
                features_dict_ = self.handler.bin_process_merging(features_dict)
                bins_dict = self.tool.convert_bins_dict(self.features, features_dict_)
            else:
                logger.info(f"{LOG_PREFIX}{role}进行合并分箱环节")
                guest_nid = self.params.get("guest_nid")
                data_transfer = self.params.get("data_transfer")
                send_event_name = self.params.get("send_features_dict_event_name")
                get_event_name = self.params.get("get_bins_dict_event_name")

                logger.info(f"{LOG_PREFIX}{role}发送密文的特征字典")
                send_event = getattr(data_transfer["algo_data_transfer"], send_event_name, None)
                if send_event is None:
                    raise ValueError(f"发送密文的特征字典事件{send_event_name}不存在")
                send_event.send_by_nid(guest_nid, (features_dict, self.features),
                                       data_transfer["ctx"], data_transfer["job_id"], data_transfer["curr_nid"])

                logger.info(f"{LOG_PREFIX}{role}接收合并分箱结果")
                get_event = getattr(data_transfer["algo_data_transfer"], get_event_name, None)
                if get_event is None:
                    raise ValueError(f"接收合并分箱结果事件{get_event_name}不存在")
                bins_dict = get_event.get(data_transfer["listener"], data_transfer["job_id"], guest_nid)
        return bins_dict

    def get_features_dict(self) -> Dict[str, Any]:
        """get features dict

        Returns:
            Dict[str, Any]: {"feature": {"success": 1, "msg": "", "result": group_result}...}
        """
        if self.bin_type == BinType.CHIMERGE_BIN.name and self.params.get("role") == "HOST":
            return self.handler.bin_process_host(log=self.log)
        else:
            return self.handler.bin_process(log=self.log)

    @staticmethod
    def get_bins_dict_by_name(features: Dict[str, Any],
                              features_dict: Dict[str, Any],
                              data_name: str) -> Dict[str, Any]:
        """get bins dict by name

        Args:
            features (Dict[str,Any]): {"feature": 0, ...}
            features_dict (Dict[str,Any]): {"feature": {}, ...}
            data_name (str): features_dict中特征的dataframe name

        Returns:
            Dict[str,Any]: {"feature": List[Any], ...}
        """
        return Tool.convert_bins_dict(features, features_dict, data_name)

    @staticmethod
    def chimerge_bin_assist_host(log: Callable,
                                 flnodes_tuple: Dict[str, str],
                                 priv: str,
                                 data_transfer: Dict[str, Any]):
        """多方，用于GUEST方协助HOST进行卡方分箱

        Args:
            log (Callable): 日志
            flnodes_tuple (Dict[str, str]): 其他节点信息，{nid: nid}
            priv (str): 私钥
            data_transfer (Dict[str, Any]): 通信集合
                                           {"algo_data_transfer": self.algo_data_transfer,
                                            "listener": self.listener,
                                            "job_id": self.job_id,
                                            "ctx": self.ctx,
                                            "curr_nid": self.curr_nid}
        """
        ChimergeBin.bin_process_assist_host(log, flnodes_tuple, priv, data_transfer)

    @staticmethod
    def merging_assist_host(bin_type: str,
                            priv: str,
                            host_nid: str,
                            get_features_dict_event_name: str,
                            send_bins_dict_event_name: str,
                            data_transfer: Dict[str, Any],
                            con_min_samples=None,
                            cat_min_samples=None):
        """多方，用于GUEST方协助HOST方进行合并分箱，计算分箱字典

        Args:
            bin_type (str): 分箱类型
            priv (str): 私钥
            host_nid (str): host node id
            get_features_dict_event_name (str): 接收features_dict的事件名
            send_bins_dict_event_name (str): 发送bins_dict的事件名
            data_transfer (Dict[str, Any]): 通信集合
                                           {"algo_data_transfer": self.algo_data_transfer,
                                            "listener": self.listener,
                                            "job_id": self.job_id,
                                            "ctx": self.ctx,
                                            "curr_nid": self.curr_nid}
            con_min_samples (Any): 连续特征最小样本量，没有此属性为None
            cat_min_samples (Any): 离散特征最小样本量，没有此属性为None
        """
        logger.info(f"{LOG_PREFIX}接收HOST发送的加密数据")
        get_event = getattr(data_transfer["algo_data_transfer"], get_features_dict_event_name, None)
        if get_event is None:
            raise ValueError(f"接收HOST发送的加密数据事件{get_features_dict_event_name}不存在")
        features_dict, features = get_event.get(data_transfer["listener"], data_transfer["job_id"], host_nid)

        logger.info(f"{LOG_PREFIX}对加密数据进行解密")
        de_features_dict = Tool.decrypt_features_dict(features_dict, features, priv)

        logger.info(f"{LOG_PREFIX}计算分箱字典")
        de_features_dict_ = Tool.bins_merging(bin_type, features, de_features_dict, con_min_samples, cat_min_samples)

        logger.info(f"{LOG_PREFIX}生成分箱区间")
        bins_dict = Tool.convert_bins_dict(features, de_features_dict_)

        logger.info(f"{LOG_PREFIX}发送分箱字典数据")
        send_event = getattr(data_transfer["algo_data_transfer"], send_bins_dict_event_name, None)
        if send_event is None:
            raise ValueError(f"发送分箱字典数据事件{send_bins_dict_event_name}不存在")
        send_event.send_by_nid(host_nid, bins_dict,
                               data_transfer["ctx"], data_transfer["job_id"], data_transfer["curr_nid"])
