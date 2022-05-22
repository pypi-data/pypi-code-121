from typing import Any, Callable, Dict

import pandas as pd
from joblib import Parallel, delayed

from .constants import LOG_PREFIX
from .enums import BinType, Distribution
from .log_utils import get_fmpc_logger
from .tool import Tool
from .wrap_utils import exec_except, exec_log, exec_time

logger = get_fmpc_logger(__name__)


class DistanceBin:
    """等距分箱

    Args:
        label (str): 标签
        features (Dict[str,int]): 特征集
        df (pd.DataFrame): 分箱数据源

        bins (Any): 等距数
        min_samples (int): 最小样本量
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

        self.bins = 10
        self.min_samples = 100
        self.parallel_info = None

        self.tool = Tool()
        self.preprocess(kwargs)

    @exec_time
    @exec_except
    def preprocess(self, kwargs):
        """preprocess"""
        self._check()
        self._parse_params(kwargs)

    def _check(self):
        """check"""
        distribution_lst = list(set(self.features.values()))
        kinds = len(distribution_lst)
        if kinds != 1 or distribution_lst[0] != Distribution.CONTINUOUS.value:
            raise ValueError("等距分箱只支持连续型特征")

    def _parse_params(self, kwargs):
        """parse params"""
        if kwargs.get("bins"):
            self.bins = kwargs.get("bins")
        if kwargs.get("min_samples"):
            self.min_samples = kwargs.get("min_samples")
        if kwargs.get("parallel_info"):
            self.parallel_info = kwargs.get("parallel_info")

    @exec_log("等距分箱计算")
    def bin_process(self,
                    log: Callable = None) -> Dict[str, Any]:
        """等距分箱计算

        Args:
            log (Callable, optional): 日志

        Returns:
            Dict[str, Any]: {"feature": {"success": 1, "msg": "", "result": group_result}...}
        """
        features_dict = {}
        if self.parallel_info.get("parallel"):
            log(f"{LOG_PREFIX}并行等距分箱计算")
            features_dict = self._features_bin_parallel()
        else:
            log(f"{LOG_PREFIX}等距分箱计算")
            df_ = self.df.loc[:, list(self.features.keys())+[self.label]]
            _features_bin(self.bins, self.label, df_, features_dict)
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
        results = Parallel(n_jobs=n_jobs)(delayed(_features_bin)(self.bins, self.label, df_parallel, tmp)
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
        return self.tool.bins_merging(self.static_bin_type(), self.features, features_dict, self.min_samples, None)

    @staticmethod
    def static_bin_type() -> str:
        return BinType.DISTANCE_BIN.name


@exec_time
def _features_bin(bins,
                  label: str,
                  df_parallel: pd.DataFrame,
                  features_dict: Dict[str, Any]) -> Dict[str, Any]:
    """分箱

    Args:
        bins (_type_): int, sequence of scalars, or IntervalIndex
        label (str): 标签
        df_parallel (pd.DataFrame): dataframe
        features_dict (Dict[str, Any]): 特征字典

    Returns:
        Dict[str, Any]: 特征字典
    """
    features_ = [feature for feature in df_parallel.columns if feature != label]
    for feature in features_:
        try:
            df_ = df_parallel.loc[:, [feature, label]]
            df_["x_cat"] = pd.cut(df_[feature], bins=bins, duplicates="drop")
            df_["x_cat"] = df_["x_cat"].astype("object")
            df_["x_cat"].fillna("NaN", inplace=True)
            result = df_.groupby(["x_cat"])[label].agg([("num", "count"), ("val_1", "sum")])
            features_dict[feature] = {"success": 1, "msg": "", "result": result}
        except Exception as ex:
            features_dict[feature] = {"success": 0, "msg": f"该特征等距分箱计算失败，{repr(ex)}"}
    return features_dict
