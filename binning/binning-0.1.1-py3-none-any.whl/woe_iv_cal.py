
from typing import Any, Callable, Dict, Tuple

import numpy as np
import pandas as pd
from fmpc.utils.LogUtils import get_fmpc_logger
from wares.common.binning.constants import LOG_PREFIX, NAN_QUO
from wares.common.binning.enums import Distribution
from wares.common.binning.tool import (Tool, group_cat_merge_bin,
                                       group_con_merge_bin)
from wares.common.binning.wrap_utils import exec_except, exec_log, exec_time

logger = get_fmpc_logger(__name__)


class WoeIvCal:
    """计算Woe, Iv

    Args:
        con_bin_type (str): 连续特征分箱类型
        cat_bin_type (str): 离散特征分箱类型
        features (Dict[str, int]): 特征集
        features_dict (Dict[str, Any]): 特征信息，包含特征的分箱信息

        bin_params (Dict[str, Any]): 分箱参数
        con_min_samples (int): 连续特征最小样本数
        cat_min_samples (int): 离散特征最小样本数

    Local:
        tool (Any): 工具类
    """

    def __init__(self,
                 con_bin_type: str,
                 cat_bin_type: str,
                 features: Dict[str, Any],
                 features_dict: Dict[str, Any],
                 **kwargs):
        self.con_bin_type = con_bin_type
        self.cat_bin_type = cat_bin_type
        self.features = features.copy()
        self.features_dict = features_dict

        self.bin_params = None
        self.con_min_samples = 100
        self.cat_min_samples = 100

        self.tool = Tool()
        self.preprocess(kwargs)

    @exec_time
    @exec_except
    def preprocess(self, kwargs):
        """preprocess"""
        self._check(kwargs)
        self._parse_params(kwargs)

    def _check(self, kwargs):
        """check"""
        if not self.con_bin_type:
            raise ValueError("连续特征分箱类型con_bin_type为空，请检查")

        if not self.cat_bin_type:
            raise ValueError("离散特征分箱类型cat_bin_type为空，请检查")

        if not self.features:
            raise ValueError("特征集features为空，请检查")

        if not self.features_dict:
            raise ValueError("特征字典features_dict为空，请检查")

        if not kwargs:
            raise ValueError("参数kwargs为空，请检查")

        if not kwargs.get("bin_params"):
            raise ValueError("分箱参数bin_params为空，请检查")

    def _parse_params(self, kwargs):
        """parse params"""
        self.bin_params = kwargs.get("bin_params")
        if kwargs.get("con_min_samples"):
            self.con_min_samples = kwargs.get("con_min_samples")
        if kwargs.get("cat_min_samples"):
            self.cat_min_samples = kwargs.get("cat_min_samples")

    @exec_log("计算woe,iv值")
    def get_cal_val(self,
                    log: Callable) -> Tuple[Dict[str, Any], pd.Series]:
        """获取woe,iv的计算结果

        Args:
            log (Callable): 日志函数

        Returns:
            Tuple[pd.Series, Dict[str, Any]]: iv值，woe值
        """
        woe_dict = {}
        iv_lst = []
        fe_features = []
        for feature, distribution in self.features.items():
            if self.features_dict[feature].get("success") == 0:
                woe_dict[feature] = self.features_dict[feature]
                fe_features.append(feature)
                continue
            try:
                df = self.features_dict[feature].get("result")
                if distribution == Distribution.CONTINUOUS.value:
                    df_ = group_con_merge_bin(df, self.con_bin_type, self.con_min_samples)
                    nan = "NaN"
                else:
                    df_ = group_cat_merge_bin(df, self.cat_bin_type, self.cat_min_samples)
                    df_.reset_index(inplace=True)
                    nan = NAN_QUO
                self._update_feature_dict_result(nan, df_)
                feature_iv = np.round(df_["iv"].sum(), 6)
                iv_lst.append(feature_iv)
                df_result = df_.loc[:, ["x_cat", "num", "odds", "woe", "iv", "positive", "negative"]]
                bin_id, bin_param, feature_distribute_type = self._get_bin_info(distribution, self.bin_params)
                woe_dict[feature] = {"success": 1,
                                     "msg": "",
                                     "woe_table": df_result,
                                     "binId": bin_id,
                                     "binParam": bin_param,
                                     "featureDistributeType": feature_distribute_type}
            except Exception as ex:
                fe_features.append(feature)
                woe_dict[feature] = {"success": 0,
                                     "msg": f"该特征计算失败，{repr(ex)}",
                                     "binId": None,
                                     "binParam": None,
                                     "featureDistributeType": None}
        if fe_features:
            log(f"{LOG_PREFIX}计算woe,iv值完成，异常特征：{fe_features}")
        
        for feature in fe_features:
            self.features.pop(feature)
        iv_ser = pd.Series(iv_lst, index=self.features)
        return (woe_dict, iv_ser)

    def _get_bin_info(self,
                      distribution: int,
                      bin_params: Dict[str, Any]) -> Tuple[str, Dict[str, Any], str]:
        """获取分箱参数信息

        Args:
            distribution (int): 特征分布类型
            bin_params (Dict[str, Any]): 分箱参数

        Returns:
            Tuple[str, Dict[str, Any], str]: 分箱参数
        """
        if distribution == Distribution.CONTINUOUS.value:
            name = Distribution.CONTINUOUS.name
            bin_id = bin_params.get(name).get("binId")
            bin_param = bin_params.get(name).get("binParam")
            feature_distribute_type = name
        else:
            name = Distribution.DISCRETE.name
            bin_id = bin_params.get(name).get("binId")
            bin_param = bin_params.get(name).get("binParam")
            feature_distribute_type = name
        return (bin_id, bin_param, feature_distribute_type)

    def _update_feature_dict_result(self,
                                    nan: str,
                                    df_: pd.DataFrame) -> None:
        """更新特征字典的结果数据

        Args:
            nan (str): NaN形式
            df_ (pd.DataFrame): dataframe
        """
        # 1. 后续会自动合并组内没有类别的箱，应该默认没有的类别加1个类别，而不是合并
        # 2. 样本数, odds, 比例等不变
        self._adjust_aggregation_result(df_)
        df_["val_0_adjust"] = df_["num_adjust"] - df_["val_1_adjust"]

        # 获取所有的0和1取值数
        sum_0 = df_["val_0_adjust"].sum()
        sum_1 = df_["val_1_adjust"].sum()

        # 获取正例占比和负例占比
        df_["positive"] = np.round(df_["val_1"] / df_["num"], 10)
        df_["negative"] = np.round(df_["val_0"] / df_["num"], 10)

        # 判断条件: 是否含缺失值且缺失值单独一箱y样本全1或者全0
        nan_x = ((df_["x_cat"] == NAN_QUO) | (df_["x_cat"] == "NaN")) & (
            (df_["positive"] == 1) | (df_["positive"] == 0))
        if len(nan_x.value_counts().tolist()) == 1:
            # 计算每一组的iv值,及woe
            df_["woe"], df_["iv"] = self._get_woe_iv(df_["val_1_adjust"], df_["val_0_adjust"], sum_1, sum_0)
            df_["odds"] = np.round(df_["val_1"] / df_["val_0"], 10)
        else:
            df_null = df_[nan_x]
            df_not_null = df_[~nan_x]
            df_["woe"], df_["iv"] = self._get_woe_iv(
                df_not_null["val_1_adjust"], df_not_null["val_0_adjust"], sum_1, sum_0)

            df_["odds"] = np.round(df_not_null["val_1"] / df_not_null["val_0"], 10)

            if (df_null["val_0"][df_null["x_cat"] == nan].values[0]) == 0:
                df_["iv"].fillna(df_["iv"][df_["odds"] == df_["odds"].max()].values[0], inplace=True)
                df_["woe"].fillna(df_["woe"][df_["odds"] == df_["odds"].max()].values[0], inplace=True)
                df_["odds"].fillna(df_["odds"].max(), inplace=True)
            else:
                df_["iv"].fillna(df_["iv"][df_["odds"] == df_["odds"].min()].values[0], inplace=True)
                df_["woe"].fillna(df_["woe"][df_["odds"] == df_["odds"].min()].values[0], inplace=True)
                df_["odds"].fillna(df_["odds"].min(), inplace=True)

    def _get_woe_iv(self,
                    val_1: int,
                    val_0: int,
                    sum_1: int,
                    sum_0: int) -> Tuple[float, float]:
        """根据正负样本两类标签值及其统计量计算woe,iv

        Args:
            val_1 (int): 正样本的值
            val_0 (int): 负样本的值
            sum_1 (int): 正样本所有值之和
            sum_0 (int): 负样本所有值之和

        Raises:
            ZeroDivisionError: 除数为0错误

        Returns:
            Tuple[float, float]: woe,iv
        """
        if sum_1 == 0 or sum_0 == 0:
            raise ZeroDivisionError("样本集中只有一类样本，无法计算woe,iv值")

        event = val_1 / sum_1
        non_event = val_0 / sum_0

        woe = np.round(np.log(event / non_event), 6)
        iv = np.round((event - non_event) * woe, 6)
        return (woe, iv)

    def _adjust_aggregation_result(self,
                                   df: pd.DataFrame) -> None:
        """adjust catagory aggregation result, fill one catagory when the num of catagory is 0

        Args:
            df (pd.DataFrame): catagory aggregation result
        """
        df[["num_adjust", "val_1_adjust"]] = df.apply(self._fill_category, axis=1, result_type="expand")

    @staticmethod
    def _fill_category(ser: pd.Series) -> Tuple[int, int]:
        """fill catagory when the num of catagory is 0

        Args:
            ser (pd.Series): the series of catagory aggregation result

        Returns:
            Tuple[int, int]: new_num, new_val_1
        """
        num = ser["num"]
        val_1 = ser["val_1"]

        if num == 0 and val_1 == 0:
            num = 2
            val_1 = 1
        elif num == val_1:
            num = num + 1
        elif val_1 == 0:
            num = num + 1
            val_1 = 1
        return (num, val_1)
