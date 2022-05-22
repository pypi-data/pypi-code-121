from typing import Any, Callable, Dict

import pandas as pd
from joblib import Parallel, delayed

from .constants import LOG_PREFIX
from .enums import BinType, Distribution
from .log_utils import get_fmpc_logger
from .tool import Tool
from .wrap_utils import exec_except, exec_log, exec_time

logger = get_fmpc_logger(__name__)


class FrequencyBin:
    """等频分箱

    Args:
        label (str): 标签
        features (Dict[str,int]): 特征集
        df (pd.DataFrame): 分箱数据源

        q (Any): 等频数
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

        self.q = 10
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
            raise ValueError("等频分箱只支持连续型特征")

    def _parse_params(self, kwargs):
        """parse params"""
        if kwargs.get("q"):
            self.q = kwargs.get("q")
        if kwargs.get("parallel_info"):
            self.parallel_info = kwargs.get("parallel_info")

    @exec_log("等频分箱计算")
    def bin_process(self,
                    log: Callable = None) -> Dict[str, Any]:
        """等频分箱计算

        Args:
            log (Callable, optional): 日志

        Returns:
            Dict[str, Any]: {"feature": {"success": 1, "msg": "", "result": group_result}...}
        """
        features_dict = {}
        if self.parallel_info.get("parallel"):
            log(f"{LOG_PREFIX}并行等频分箱计算")
            features_dict = self._features_bin_parallel()
        else:
            log(f"{LOG_PREFIX}等频分箱计算")
            df_ = self.df.loc[:, list(self.features.keys())+[self.label]]
            _features_bin(self.q, self.label, df_, features_dict)
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
        results = Parallel(n_jobs=n_jobs)(delayed(_features_bin)(self.q, self.label, df_parallel, tmp)
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
        return self.tool.bins_merging(self.static_bin_type(), self.features, features_dict, None, None)

    @staticmethod
    def static_bin_type() -> str:
        return BinType.FREQUENCY_BIN.name


@exec_time
def _features_bin(q,
                  label: str,
                  df_parallel: pd.DataFrame,
                  features_dict: Dict[str, Any]) -> Dict[str, Any]:
    """分箱

    Args:
        q (_type_): int or list-like of float
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
            df_["x_cat"] = pd.qcut(df_[feature], q=q, duplicates="drop")
            df_["x_cat"] = df_["x_cat"].astype("object")
            df_["x_cat"].fillna("NaN", inplace=True)
            result = df_.groupby(["x_cat"])[label].agg([("num", "count"), ("val_1", "sum")])
            features_dict[feature] = {"success": 1, "msg": "", "result": result}
        except Exception as ex:
            features_dict[feature] = {"success": 0, "msg": f"该特征等频分箱计算失败，{repr(ex)}"}
    return features_dict
