import json
from typing import Any, Callable, Dict

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from .constants import LOG_PREFIX
from .enums import BinType, Distribution
from .log_utils import get_fmpc_logger
from .tool import Tool, get_cat_feature_bin, get_con_feature_bin
from .wrap_utils import exec_except, exec_log, exec_time

logger = get_fmpc_logger(__name__)


class CustomBin:
    """自定义分箱

    Args:
        label (str): 标签
        features (Dict[str,int]): 特征集
        df (pd.DataFrame): 分箱数据源

        con_param (Any): 连续特征参数
        con_min_samples (int): 连续特征最小样本量
        cat_param (Any): 离散特征参数
        cat_min_samples (int): 离散特征最小样本量
        parallel_info (Any): 并行信息

    Local:
        tool (Any): 工具类
    """

    def __init__(self,
                 label: str,
                 features: Dict[str, Any],
                 df: pd.DataFrame,
                 **kwargs):
        self.label = label
        self.features = features
        self.df = df

        self.con_param = None
        self.con_min_samples = 100
        self.cat_param = None
        self.cat_min_samples = 100
        self.parallel_info = None

        self.tool = Tool()
        self.preprocess(kwargs)

    @exec_time
    @exec_except
    def preprocess(self, kwargs):
        self._check(kwargs)
        self._parse_params(kwargs)

    def _check(self, kwargs):
        """check"""
        distribution_lst = list(set(self.features.values()))
        if Distribution.CONTINUOUS.value in distribution_lst and not kwargs.get("con_param"):
            raise ValueError(f"特征中存在连续特征，参数con_param为空，请检查")
        if Distribution.DISCRETE.value in distribution_lst and not kwargs.get("cat_param"):
            raise ValueError(f"特征中存在离散特征，参数cat_param为空，请检查")

    def _parse_params(self, kwargs):
        """parse params"""
        if kwargs.get("parallel_info"):
            self.parallel_info = kwargs.get("parallel_info")

        # 连续特征参数
        if kwargs.get("con_param"):
            bins_lst = [float(item) for item in kwargs.get("con_param").split(",")]
            bins_lst = list(set(bins_lst))
            bins_lst.sort()
            self.con_param = [-np.inf] + bins_lst + [np.inf]

        if kwargs.get("con_min_samples"):
            self.con_min_samples = kwargs.get("con_min_samples")

        # 离散特征参数
        if kwargs.get("cat_param"):
            bins_lst = kwargs.get("cat_param")
            self.cat_param = [] if bins_lst is None else json.loads(json.dumps(bins_lst))

        if kwargs.get("cat_min_samples"):
            self.cat_min_samples = kwargs.get("cat_min_samples")

    @exec_log("自定义分箱计算")
    def bin_process(self, log: Callable = None) -> Dict[str, Any]:
        """自定义分箱计算

        Args:
            log (Callable, optional): 日志

        Returns:
            Dict[str, Any]: {"feature": {"success": 1, "msg": "", "result": group_result}...}
        """
        features_dict = {}
        if self.parallel_info.get("parallel"):
            log(f"{LOG_PREFIX}并行自定义分箱计算")
            features_dict = self._features_bin_parallel()
        else:
            log(f"{LOG_PREFIX}自定义分箱计算")
            df_ = self.df.loc[:, list(self.features.keys()) + [self.label]]
            _features_bin(self.con_param, self.cat_param, self.features, self.label, df_, features_dict)
        return features_dict

    def _features_bin_parallel(self) -> Dict[str, Any]:
        """分箱计算，并行

        Returns:
            Dict[str, Any]: features_dict
        """
        n_parallel = self.parallel_info["n_parallel"]
        features_lst = self.parallel_info["features_lst"]

        df_parallel_lst = []
        for feature in features_lst:
            df_parallel_lst.append(self.df.loc[:, feature + [self.label]])

        tmp = {}
        n_jobs = 1 if n_parallel == 0 else n_parallel
        results = Parallel(n_jobs=n_jobs)(delayed(_features_bin)(self.con_param, self.cat_param, self.features, self.label, df_parallel, tmp)
                                          for df_parallel in df_parallel_lst)

        # 并行结果转换
        features_dict = {}
        for features_dict_ in results:
            features_dict.update(features_dict_)
        return features_dict

    def bin_process_merging(self,
                            features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """根据分箱结果进行分箱合并

        Args:
            features_dict (Dict[str, Any]): 分箱结果

        Returns:
            Dict[str, Any]: {"feature": {"success": 1/0, "msg": msg, "result": df}}
        """
        return self.tool.bins_merging(self.static_bin_type(), self.features, features_dict, self.con_min_samples, self.cat_min_samples)

    @staticmethod
    def static_bin_type() -> str:
        return BinType.CUSTOM_BIN.name


@exec_time
def _features_bin(con_param: Any,
                  cat_param: Any,
                  features: Dict[str, Any],
                  label: str,
                  df_parallel: pd.DataFrame,
                  features_dict: Dict[str, Any]) -> Dict[str, Any]:
    """分箱

    Args:
        con_param(Any): 连续特征参数，List or None
        cat_param(Any): 离散特征参数，List or None
        features(Dict[str, Any]): 特征集
        label(str): 标签
        df_parallel(pd.DataFrame): dataframe
        features_dict(Dict[str, Any]): 特征字典

    Returns:
        Dict[str, Any]: 特征字典
    """
    features_ = [feature for feature in df_parallel.columns if feature != label]
    for feature in features_:
        df_ = df_parallel.loc[:, [feature, label]]
        if features[feature] == Distribution.CONTINUOUS.value:
            features_dict[feature] = get_con_feature_bin(df_, label, feature, con_param)
        else:
            features_dict[feature] = get_cat_feature_bin(df_, label, feature, cat_param)
    return features_dict
