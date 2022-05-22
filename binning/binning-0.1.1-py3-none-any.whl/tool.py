import json
from math import ceil
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from .constants import NAN_QUO
from .enums import BinType, Distribution
from .log_utils import get_fmpc_logger

logger = get_fmpc_logger(__name__)


class Tool:
    @staticmethod
    def get_n_split_n_parallel(n_cpu, n_features):
        """根据cpu数量和特征量，计算出cpu训练特征量，并行cpu数量

        :param n_cpu: cpu数量
        :param n_features: 特征量
        :return: cpu训练特征量，并行cpu数量
        """
        if n_features < 4 or n_cpu < 4:
            n_split = n_features
            n_parallel = 1
        elif n_features <= n_cpu:
            n_split = 1
            n_parallel = n_features
        else:
            n_split = ceil(n_features / n_cpu)
            n_parallel = ceil(n_features / n_split)

        return (n_split, n_parallel)

    @staticmethod
    def data_slice(data, slice_size):
        """数据切片

        :param data: list or dict
        :param slice_size: 分组大小
        :return: []
        """
        convert_lst = []
        if isinstance(data, dict):
            for key in data:
                convert_lst.append(key)

        if isinstance(data, list):
            convert_lst = data

        if slice_size <= 0:
            return [convert_lst]

        return [convert_lst[i * slice_size:(i + 1) * slice_size] for i in range(0, ceil(len(convert_lst) / slice_size))]

    @staticmethod
    def decrypt_features_dict(feature_dict, features, priv):
        """对特征字典进行解密

        :param feature_dict: 特征字典
        :param features: 特征集
        :param priv: 密钥
        :return: 解密后的特征字典
        """
        feature_dict_de = {}
        for x in features:
            if feature_dict[x].get('success') == 0:
                feature_dict_de[x] = feature_dict[x]
                continue
            try:
                df_tmp2 = feature_dict[x].get('result')
                df_tmp = df_tmp2.copy()
                df_tmp['val_1'] = df_tmp2['val_1'].apply(lambda x: decrypting(x, priv))
                feature_dict_de[x] = {'success': 1, 'msg': '', 'result': df_tmp}
            except Exception as ex:
                feature_dict_de[x] = {'success': 0, 'msg': f'该特征字段值解密失败，{repr(ex)}'}
        return feature_dict_de

    @staticmethod
    def convert_bins_dict(features: Dict[str, Any],
                          features_dict: Dict[str, Any],
                          name: str = None) -> Dict[str, Any]:
        """根据result dict转换成bins dict

        Args:
            features (Dict[str,Any]): 特征集
            features_dict (Dict[str, Any]): 特征字典
            name (str): 数据名称

        Returns:
            Dict[str, Any]: bins dict
        """
        bins_dict = {}
        for feature, data in features_dict.items():
            success = data.get("success")
            if success == 0:
                bins_dict[feature] = None
                continue

            distribution = features[feature]
            bins_lst = []
            if name is None:
                df = data.get("result")
            else:
                df = data.get(name)
            df.reset_index(inplace=True)

            if distribution == Distribution.CONTINUOUS.value:
                _get_con_bins_lst(bins_lst, df["x_cat"])
            else:
                for _, value in df["x_cat"].items():
                    val = value.strip('"').replace('","', '\xBA').split('\xBA')
                    _update_list_drop_duplicate(bins_lst, val)
            bins_dict[feature] = bins_lst
        return bins_dict

    @staticmethod
    def bins_merging(bin_type: str,
                     features: Dict[str, Any],
                     features_dict: Dict[str, Any],
                     con_min_sample: Any,
                     cat_min_sample: Any) -> Dict[str, Any]:
        """分箱合并

        Args:
            bin_type (str): 分箱类型
            features (Dict[str, Any]): 特征集
            features_dict (Dict[str, Any]): 分箱结果
            con_min_sample (Any): 连续特征最小样本量
            cat_min_sample (Any): 离散特征最小样本量

        Returns:
            Dict[str, Any]: {"feature": {"success": 1/0, "msg": msg, "result": df}}
        """
        merge_result = {}
        for feature, distribution in features.items():
            success = features_dict[feature].get("success")
            msg = features_dict[feature].get("msg")
            if success == 0:
                df_tmp = None
            else:
                df = features_dict[feature].get("result")
                if distribution == Distribution.CONTINUOUS.value:
                    df_tmp = group_con_merge_bin(df, bin_type, con_min_sample)
                else:
                    df_tmp = group_cat_merge_bin(df, bin_type, cat_min_sample)
                    df_tmp.reset_index(inplace=True)

            merge_result[feature] = {"success": success,
                                     "msg": msg,
                                     "result": df_tmp}
        return merge_result


def _get_con_bins_lst(bins_lst: List[Any],
                      interval_ser: pd.Series) -> None:
    """获取连续特征的分箱列表

    Args:
        bins_lst (List[Any]): 分箱列表
        interval_ser (pd.Series): 区间series
    """
    has_nan = False
    if "NaN" in interval_ser.values:
        has_nan = True

    num = len(interval_ser.index)
    for idx, interval in interval_ser.items():
        if idx == 0 and num != 1:
            _update_list_drop_duplicate(bins_lst, -np.inf)
            _update_list_drop_duplicate(bins_lst, interval.right)
        elif (has_nan and idx == num - 2 and num != 1) or ((not has_nan) and idx == num - 1 and num != 1):
            _update_list_drop_duplicate(bins_lst, interval.left)
            _update_list_drop_duplicate(bins_lst, np.inf)
        else:
            if interval == "NaN":
                _update_list_drop_duplicate(bins_lst, "NaN")
            else:
                _update_list_drop_duplicate(bins_lst, interval.left)
                _update_list_drop_duplicate(bins_lst, interval.right)


def _update_list_drop_duplicate(lst: List[Any],
                                item: Any) -> None:
    """更新列表不添加重复元素

    Args:
        lst (List[Any]): 列表
        item (Any): 元素
    """
    if item not in lst:
        lst.append(item)


def group_con_merge_bin(df_tmp, bin_type, con_min_sample):
    """连续特征分箱合并，如相类似的箱数进行合并

    :param df_tmp: dataframe
    :param bin_type: 分箱类型
    :param con_min_sample: 连续特征最小样本量
    :return: df
    """
    df_tmp_nan = None
    df_tmp['val_0'] = df_tmp['num'] - df_tmp['val_1']
    df_tmp.reset_index(inplace=True)
    df_tmp['x_cat'] = df_tmp['x_cat'].astype('object')
    is_nan = False
    if df_tmp.loc[df_tmp.index.max(), 'x_cat'] == 'NaN':
        is_nan = True
        df_tmp_nan = df_tmp.loc[[df_tmp.index.max()]]
        df_tmp.drop([df_tmp.index.max()], inplace=True)

    # 对于不合适的分组，将其合并到别的组
    for i in df_tmp.index:
        if len(df_tmp) == 1:
            break
        if bin_type == BinType.FREQUENCY_BIN.name:
            judge = False
        else:
            if df_tmp.loc[i, 'num'] < con_min_sample:
                judge = True
            else:
                judge = False
        _con_merge_bin(i, judge, df_tmp)
    if is_nan:
        df_tmp2 = pd.concat([df_tmp, df_tmp_nan], ignore_index=True)
        return df_tmp2
    return df_tmp


def _con_merge_bin(idx, is_merge, df_tmp):
    """连续特征合并分箱

    :param idx: 索引
    :param is_merge: 是否合并
    :param df_tmp: 样本dataframe
    """
    if is_merge:
        if idx == df_tmp.index.max():
            pos = len(df_tmp) - 2
            indx = df_tmp.index[pos]
            df_tmp.loc[indx, 'val_0'] = df_tmp.loc[indx, 'val_0'] + df_tmp.loc[idx, 'val_0']
            df_tmp.loc[indx, 'val_1'] = df_tmp.loc[indx, 'val_1'] + df_tmp.loc[idx, 'val_1']
            df_tmp.loc[indx, 'num'] = df_tmp.loc[indx, 'num'] + df_tmp.loc[idx, 'num']
            tmp_interval = pd.Interval(left=df_tmp.loc[indx, 'x_cat'].left, right=df_tmp.loc[idx, 'x_cat'].right)
            df_tmp.loc[indx, 'x_cat'] = tmp_interval
            df_tmp.drop([idx], axis=0, inplace=True)
        else:
            df_tmp.loc[idx + 1, 'val_0'] = df_tmp.loc[idx + 1, 'val_0'] + df_tmp.loc[idx, 'val_0']
            df_tmp.loc[idx + 1, 'val_1'] = df_tmp.loc[idx + 1, 'val_1'] + df_tmp.loc[idx, 'val_1']
            df_tmp.loc[idx + 1, 'num'] = df_tmp.loc[idx + 1, 'num'] + df_tmp.loc[idx, 'num']
            tmp_interval = pd.Interval(left=df_tmp.loc[idx, 'x_cat'].left, right=df_tmp.loc[idx + 1, 'x_cat'].right)
            df_tmp.loc[idx + 1, 'x_cat'] = tmp_interval
            df_tmp.drop([idx], axis=0, inplace=True)


def group_cat_merge_bin(df_tmp, bin_type, cat_min_sample):
    """离散特征分箱合并，如相类似的箱数进行合并

    :param df_tmp: 数据源
    :param bin_type: 分箱类型
    :param cat_min_sample: 离散特征最小样本量
    :return: df
    """
    df_tmp_nan = None
    df_tmp['val_0'] = df_tmp['num'] - df_tmp['val_1']
    if bin_type == BinType.ENUMERATE_BIN.name or bin_type == BinType.CUSTOM_BIN.name:
        return df_tmp

    df_tmp['odds'] = np.round(df_tmp['val_1'] / df_tmp['val_0'], 10)
    df_tmp = df_tmp.reset_index()
    df_tmp['x_cat'] = df_tmp['x_cat'].astype('object')
    is_nan = False
    for i in df_tmp.index:
        if df_tmp.loc[i, 'x_cat'] == NAN_QUO:
            is_nan = True
            df_tmp_nan = df_tmp.loc[[i]]
            df_tmp.drop([i], inplace=True)
    df_tmp = df_tmp.reset_index(drop=True)
    _cat_merge_bin(cat_min_sample, df_tmp)
    if is_nan:
        df_tmp_s = pd.concat([df_tmp, df_tmp_nan], ignore_index=True)
        return df_tmp_s
    return df_tmp


def _cat_merge_bin(cat_min_sample, df_tmp):
    """离散特征合并分箱

    :param cat_min_sample: 离散特征最小样本量
    :param df_tmp: dataframe
    """
    judge_set = set()
    while True:
        if len(df_tmp) == 1 or len(set(judge_set)) == 1:
            break
        odds_list = list()
        index = df_tmp.shape[0]
        odds = None
        judge_set.clear()
        for i in df_tmp.index:
            if df_tmp.loc[i, 'num'] < cat_min_sample:
                judge_set.add(True)
                index = min(i, index)
                odds = df_tmp.loc[index, 'odds']
                odds_list.append(df_tmp.loc[i, 'odds'])
            else:
                judge_set.add(False)
                odds_list.append(df_tmp.loc[i, 'odds'])

        _update_cat_df(judge_set, odds_list, index, odds, df_tmp)


def _update_cat_df(judge_set, odds_list, index, odds, df_tmp):
    """更新离散特征的df

    :param judge_set: set(True/False)
    :param odds_list: [df['odds'], df['odds']]
    :param index: 索引
    :param odds: df['odds']
    :param df_tmp: dataframe
    """
    odds_abs_json = {}
    if len(judge_set) > 1:
        for i, iodds in enumerate(odds_list):
            if i != index:
                odds_abs_json[i] = np.round(abs(odds - iodds), 10)

        min_index = min(odds_abs_json.keys(), key=(lambda k: odds_abs_json[k]))
        df_tmp.loc[index, 'val_0'] = df_tmp.loc[index, 'val_0'] + df_tmp.loc[min_index, 'val_0']
        df_tmp.loc[index, 'val_1'] = df_tmp.loc[index, 'val_1'] + df_tmp.loc[min_index, 'val_1']
        df_tmp.loc[index, 'num'] = df_tmp.loc[index, 'num'] + df_tmp.loc[min_index, 'num']
        tmp_interval = df_tmp.loc[index, 'x_cat'] + ',' + df_tmp.loc[min_index, 'x_cat']
        df_tmp.loc[index, 'x_cat'] = tmp_interval
        df_tmp.drop([min_index], axis=0, inplace=True)
        df_tmp['odds'] = np.round(df_tmp['val_1'] / df_tmp['val_0'], 10)
        df_tmp.reset_index(drop=True, inplace=True)


def _get_cat_enums_lst(x_enums: Dict[Any, Any],
                       bins: List[Any]) -> List[Any]:
    """离散特征，把不在bins中而在x_enums中的key加入到bins中

    Args:
        x_enums(Dict[Any, Any]): 特征枚举
        bins(List[Any]): 分箱参数

    Returns:
        List[Any]: list([iterable])
    """
    merge_enums = []
    for enums_lst in bins:
        for key in enums_lst:
            merge_enums.append(key)
    for key in x_enums:
        if key not in merge_enums:
            bins.append(key)
    return bins


def _merge_categorical(feature: str,
                       cat_enums_lst: List[Any],
                       df: pd.DataFrame) -> pd.DataFrame:
    """离散特征数据映射，把特征feature的信息(cat_enums_lst)更新到df

    Args:
        feature(str): 特征
        cat_enums_lst(List[Any]): 枚举list
        df(pd.DataFrame): dataframe

    Returns:
        pd.DataFrame: new dataframe
    """
    tmp_dic = {}
    df2 = df.copy()
    for i in cat_enums_lst:
        if type(i) == list:
            for j in i:
                tmp_dic[j] = ','.join('"' + item + '"' for item in i)
        else:
            tmp_dic[i] = '"' + i + '"'
    # 特征类型转为str, 整型离散特征会映射不了
    df2[feature] = df[feature].apply(str).map(tmp_dic)
    return df2


def get_con_feature_bin(df: pd.DataFrame,
                        label: str,
                        feature: str,
                        con_param: List[str]) -> Dict[str, Any]:
    """连续特征分箱

    Args:
        df(pd.DataFrame): dataframe
        label(str): 标签
        feature(str): 特征
        con_param(List[str]): 分箱参数

    Returns:
        Dict[str, Any]: 分箱结果，{"feature": {"success": 1, "msg": "", "result": group_result}...}
    """
    try:
        df["x_cat"] = pd.cut(df[feature], con_param)
        df["x_cat"] = df["x_cat"].astype("object")
        df["x_cat"].fillna("NaN", inplace=True)
        result = df.groupby(["x_cat"])[label].agg([("num", "count"), ("val_1", "sum")])
        return {"success": 1, "msg": "", "result": result}
    except Exception as ex:
        return {"success": 0, "msg": f"该连续特征自定义分箱计算失败，{repr(ex)}"}


def get_cat_feature_bin(df: pd.DataFrame,
                        label: str,
                        feature: str,
                        cat_param: List[str]) -> Dict[str, Any]:
    """离散特征分箱

    Args:
        df(pd.DataFrame): dataframe
        label(str): 标签
        feature(str): 特征
        cat_param(List[str]): 离散特征分箱参数

    Returns:
        Dict[str, Any]: 分箱结果，{"feature": {"success": 1, "msg": "", "result": group_result}...}
    """
    try:
        df[feature] = df[feature].astype("object")  # 离散类型转换object
        df[feature].fillna("NaN", inplace=True)
        x_enums = json.loads(df[feature].value_counts().to_json())
        cat_enums_lst = _get_cat_enums_lst(x_enums, cat_param)
        df_tmp = _merge_categorical(feature, cat_enums_lst, df)
        df_tmp["x_cat"] = df_tmp[feature]
        df_tmp["x_cat"] = df_tmp["x_cat"].astype("object")
        df_tmp["x_cat"].fillna(NAN_QUO, inplace=True)
        result = df_tmp.groupby(["x_cat"])[label].agg([("num", "count"), ("val_1", "sum")])
        return {"success": 1, "msg": "", "result": result}
    except Exception as ex:
        return {"success": 0, "msg": f"该离散特征自定义分箱计算失败,{repr(ex)}"}


def decrypting(val: Any,
               priv: Any) -> int:
    """解密

    Args:
        val (Any): 待解密的value
        priv (Any): 私钥

    Returns:
        int: 解密后的值
    """
    try:
        de_val = priv.decrypt(val)
    except Exception:
        return 0
    else:
        return np.round(de_val, 0)
