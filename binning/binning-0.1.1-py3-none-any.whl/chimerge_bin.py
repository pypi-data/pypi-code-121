import copy
from itertools import combinations
from typing import Any, Callable, Dict, List, Tuple

import numpy as np
import pandas as pd
from joblib import Parallel, delayed

from .constants import LOG_PREFIX, MIN_BINS
from .enums import BinType, Distribution
from .log_utils import get_fmpc_logger
from .tool import Tool, decrypting, get_cat_feature_bin, get_con_feature_bin
from .wrap_utils import exec_except, exec_log, exec_time

logger = get_fmpc_logger(__name__)


class ChimergeBin:
    """卡方分箱

    Args:
        label (str): 标签
        features (Dict[str,int]): 特征集
        df (pd.DataFrame): 分箱数据源

        con_params (Dict[str,Any]): 连续特征分箱参数
        cat_params (Dict[str,Any]): 离散特征分箱参数
        parallel_info (Any): 并行信息
        guest_nid (Any): guest nodeid
        data_transfer (Any): 通信集合
                            {"algo_data_transfer": self.algo_data_transfer,
                            "listener": self.listener,
                            "job_id": self.job_id,
                            "ctx": self.ctx,
                            "curr_nid": self.curr_nid}

    Local:
        hex_features_dict (Any): 特征编码的特征字典
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

        self.con_params = {"bins": 10, "threshold": 3.84, "min_samples": 100}
        self.cat_params = {"bins": 10, "threshold": 3.84, "min_samples": 100}

        self.parallel_info = None
        self.guest_nid = None
        self.data_transfer = None

        self.hex_features_dict = None

        self.tool = Tool()
        self.preprocess(kwargs)

    @exec_time
    @exec_except
    def preprocess(self, kwargs):
        """preprocess"""
        self._validate()
        self._parse_params(kwargs)

    def _validate(self):
        """validate"""
        if len(self.df.index) <= MIN_BINS:
            raise ValueError("样本数据量小于最小箱数，无法进行卡方分箱")

    def _parse_params(self, kwargs):
        """parse params"""
        if kwargs.get("parallel_info"):
            self.parallel_info = kwargs.get("parallel_info")
        if kwargs.get("guest_nid"):
            self.guest_nid = kwargs.get("guest_nid")
        if kwargs.get("data_transfer"):
            self.data_transfer = kwargs.get("data_transfer")

        # 连续特征参数
        if kwargs.get("con_bins"):
            self.con_params["bins"] = kwargs.get("con_bins")
        if kwargs.get("con_threshold"):
            self.con_params["threshold"] = kwargs.get("con_threshold")
        if kwargs.get("con_min_samples"):
            self.con_params["min_samples"] = kwargs.get("con_min_samples")

        # 离散特征参数
        if kwargs.get("cat_bins"):
            self.cat_params["bins"] = kwargs.get("cat_bins")
        if kwargs.get("cat_threshold"):
            self.cat_params["threshold"] = kwargs.get("cat_threshold")
        if kwargs.get("cat_min_samples"):
            self.cat_params["min_samples"] = kwargs.get("cat_min_samples")

        self.hex_features_dict = self.__convert_hex_features_dict()

    def __convert_hex_features_dict(self):
        """hex features dict"""
        hex_features_dict = {}
        for feature, distribution in self.features.items():
            hex_feature = feature.encode("utf-8").hex()
            feature_chi2_dict = {"feature": feature, "distribution": distribution, "chi2_params": {}, "chi2_values": {}}
            if distribution == Distribution.CONTINUOUS.value:
                feature_chi2_dict["chi2_params"] = self.con_params
                hex_features_dict[hex_feature] = feature_chi2_dict
            else:
                feature_chi2_dict["chi2_params"] = self.cat_params
                hex_features_dict[hex_feature] = feature_chi2_dict
        return hex_features_dict

    @exec_log("卡方分箱计算")
    def bin_process(self, log: Callable = None) -> Dict[str, Any]:
        """卡方分箱计算

        Args:
            log (Callable, optional): 日志

        Returns:
            Dict[str, Any]: {"feature": {"success": 1, "msg": "", "result": group_result}...}
        """
        logger.info(f"{LOG_PREFIX}(guest)卡方分箱开始，发送features_a:{self.hex_features_dict}")

        sep_vals = {}
        for _, feature_info in self.hex_features_dict.items():
            feature = feature_info["feature"]
            if feature_info["distribution"] == Distribution.CONTINUOUS.value:
                group_dict_y = self._con_compute_chi2_info(feature_info)
                ser_chi2 = _cal_all_chi2(group_dict_y)
                feature_info["chi2_values"]["ser_chi2"] = ser_chi2
                sep_vals[feature] = self._get_y_sep_val(feature_info, log)
            else:
                group_dict_categorical = self._cat_compute_chi2_info(feature_info)
                ser_chi2_categorical = _cal_all_chi2(group_dict_categorical)
                feature_info["chi2_values"]["ser_chi2"] = ser_chi2_categorical
                sep_vals[feature] = self._get_y_sep_val(feature_info, log)
        return self._get_features_dict(sep_vals)

    def _get_y_sep_val(self, feature_info, log):
        """获取y方卡方信息sep_vals

        :param feature_info: 特征信息 {}
        :param log: 日志
        :return: sep_val
        """
        feature = feature_info["feature"]
        distribution = feature_info["distribution"]
        ser_chi2 = feature_info["chi2_values"]["ser_chi2"]

        # 原单特征卡方分箱，如果卡方值为None, 会抛出异常
        # 现适配多特征，不能抛出异常，后续计算此特征还是会计算失败
        if ser_chi2 is None:
            sep_val = None
        else:
            if distribution == Distribution.CONTINUOUS.value:
                self._con_feature_compute_chi2(feature_info, log)
                df = feature_info["chi2_values"]["df"]
                sep_val = self._get_sep_val(df['sep'])
            else:
                self._cat_feature_compute_chi2(feature_info, log)
                dfc = feature_info["chi2_values"]["dfc"]
                sep_val = dfc[feature].tolist()
        return sep_val

    def _con_feature_compute_chi2(self, feature_info, log):
        """连续型特征，卡方分箱计算

        :param feature_info: 特征信息 {}
        :param log: 日志
        """
        feature = feature_info["feature"]
        max_box = feature_info["chi2_params"]["bins"]
        chi2_threshold = feature_info["chi2_params"]["threshold"]
        ser_chi2 = feature_info["chi2_values"]["ser_chi2"]
        df = feature_info["chi2_values"]["df"]

        key_a = None
        j = 0
        while True:
            j += 1
            log(f"{LOG_PREFIX}卡方分箱-特征{feature}-第{j}次迭代")
            min_chi2, min_chi2_index = self.__get_min_chi2(ser_chi2)
            logger.info(f"===>>(连续)退出循环条件:chi2_threshold:{chi2_threshold},minChi2:{min_chi2}")
            logger.info(f"===>>(连续)退出循环条件:ser_chi2:{ser_chi2},max_box:{max_box}")
            if _threshold_check(chi2_threshold, min_chi2) and _bins_check(ser_chi2, max_box):
                break
            # 定位key前后的行
            pos = df.index.tolist().index(min_chi2_index)
            key_b = df.index[pos + 1]  # key_b 就是箱体合并前key_x在df中的下一行
            if min_chi2_index != df.index[0]:
                key_a = df.index[pos - 1]  # key_a 是key_x在df中的上一行
            # 合并后一行
            df.loc[min_chi2_index, "num"] = df.loc[min_chi2_index, "num"] + df.loc[key_b, "num"]
            df.loc[min_chi2_index, "val_1"] = df.loc[min_chi2_index, "val_1"] + df.loc[key_b, "val_1"]
            df.loc[min_chi2_index, "val_0"] = df.loc[min_chi2_index, "val_0"] + df.loc[key_b, "val_0"]

            df = df.drop(index=key_b, axis=0)
            ser_chi2.drop(index=min_chi2_index, inplace=True)
            # 有部分需要重新计算卡方
            if min_chi2_index != df.index[-1]:
                frame = df.iloc[[pos, pos + 1], [1, 2]].reset_index().drop(columns="index")
                ser_chi2.drop(index=key_b, inplace=True)
                chi2_val = _cal_chi2(frame)
                ser_chi2[min_chi2_index] = chi2_val
            # 如果key_x不是第一行，那key_x前一行也需要更新
            if min_chi2_index != df.index[0]:
                frame_pre = df.iloc[[pos - 1, pos], [1, 2]].reset_index().drop(columns="index")
                chi2_val2 = _cal_chi2(frame_pre)
                ser_chi2[key_a] = chi2_val2
        feature_info["chi2_values"]["df"] = df
        log(f"{LOG_PREFIX}卡方分箱-特征{feature} 计算完成,迭代次数{j}次")

    def _cat_feature_compute_chi2(self, feature_info, log):
        """离散特征，计算卡方值

        :param feature_info: 特征信息 {}
        :param log: 日志
        """
        (feature, max_box, chi2_threshold, ser_chi2_categorical, dfc, gr, gr0, m, nc) = self._get_values(feature_info)
        if dfc[feature].dtype != "object":
            dfc[feature] = dfc[feature].apply(str)
        j = 0
        while True:
            j += 1
            log(f"{LOG_PREFIX}卡方分箱-特征{feature}-第{j}次迭代")
            if ser_chi2_categorical.count() <= 1:
                break
            min_chi2_categotical, min_chi2_index_categotical = self.__get_min_chi2(ser_chi2_categorical)
            logger.info(f"===>>(离散)退出循环条件:chi2_threshold:{chi2_threshold},chi2_threshold:{min_chi2_categotical}")
            logger.info(f"===>>(离散)退出循环条件:ser_chi2_categorical:{ser_chi2_categorical},max_box:{max_box}")
            if _threshold_check(chi2_threshold, min_chi2_categotical) and _bins_check(ser_chi2_categorical, max_box):
                break
            to_merge = gr0[min_chi2_index_categotical]
            to_merge = list(to_merge)
            combine = pd.DataFrame()  # 合并后的新结果
            enums_lst = list()
            left = dfc.loc[to_merge[0], feature]
            right = dfc.loc[to_merge[1], feature]
            _update_enums_lst(enums_lst, left, right)
            combine[feature] = [enums_lst]
            combine["num"] = dfc.loc[to_merge[0], "num"] + dfc.loc[to_merge[1], "num"]
            combine["val_1"] = dfc.loc[to_merge[0], "val_1"] + dfc.loc[to_merge[1], "val_1"]
            combine["val_0"] = dfc.loc[to_merge[0], "val_0"] + dfc.loc[to_merge[1], "val_0"]
            combine.index = [nc]
            nc = nc + 1
            dfc.drop(index=to_merge, inplace=True)  # 将合并的两列从原始表格中删除
            remained_comb = list(combinations(dfc.index, 2))  # 删除后剩余组合（不需要更新的部分）
            delete_comb = list(set(gr) - set(remained_comb))
            delete_key = []
            for i in delete_comb:
                delete_key.append(gr0.index(i))  # 需要删除的卡方
            dfc = pd.concat([dfc, combine], axis=0)  # 将合并后的结果并入原始表格
            gr = list(combinations(dfc.index, 2))  # 合并后的所有组合
            to_update = list(set(gr) - set(remained_comb))  # 需要更新的部分
            update_dict_categorical = dict()
            for i, idx in enumerate(to_update):
                idx = list(idx)
                tmp = dfc.loc[idx, ["val_1", "val_0"]]
                tmp.index = [0, 1]
                update_dict_categorical[i + m] = tmp
            gr0.extend(to_update)
            m = len(gr0)
            ser_chi2_categorical.drop(index=delete_key, inplace=True)
            ser_update_categorical = _cal_all_chi2(update_dict_categorical)
            ser_chi2_categorical = pd.concat([ser_chi2_categorical, ser_update_categorical])
        feature_info["chi2_values"]["dfc"] = dfc
        log(f"{LOG_PREFIX}卡方分箱-特征{feature} 计算完成,迭代次数{j}次")

    def _con_compute_chi2_info(self, feature_info):
        """连续特征卡方分箱的初值

        :param feature_info: 特征卡方相关信息
        :return: group_dict
        """
        feature = feature_info["feature"]

        df0 = self.df.loc[:, [feature, self.label]]
        # 初始先等频拆分成100箱，然后再逐层合并
        df0['sep'] = pd.qcut(df0[feature], 100, duplicates='drop')
        df = df0.groupby('sep', sort=True)[self.label].agg([("num", "count"), ("val_1", "sum")])
        df['val_0'] = df['num'] - df['val_1']
        # 过滤分箱记录数为0的分箱
        df = df[df['num'] > 0]
        df.reset_index(inplace=True)

        group_dict_y = {}
        for i in range(len(df.index) - 1):
            df_reindex = df.loc[i:i + 1, ['val_1', 'val_0']]
            df_reindex.reset_index(inplace=True)
            df_reindex.drop(columns='index', inplace=True)
            group_dict_y[i] = df_reindex

        feature_info["chi2_values"]["df"] = df
        return group_dict_y

    def _cat_compute_chi2_info(self, feature_info):
        """离散特征卡方分箱的初值

        :param df_b: dataframe
        :param feature_info: 特征卡方相关信息
        :param label_b: 标签
        :return: group_dict
        """
        feature = feature_info["feature"]

        df1 = self.df.loc[:, [feature, self.label]]
        dfc = df1.groupby(feature)[self.label].agg([("num", "count"), ("val_1", "sum")])
        dfc['val_0'] = dfc['num'] - dfc['val_1']
        dfc.reset_index(inplace=True)
        nc = len(dfc)
        gr0 = list(combinations(dfc.index, 2))
        gr = gr0.copy()
        m = len(gr0)
        logger.info(f"离散特征{feature}计算卡方，遍历次数{m}")

        group_dict = {}
        for i, idx in enumerate(gr):
            idx = list(idx)
            tmp = dfc.loc[idx, ["val_1", "val_0"]]
            tmp.index = [0, 1]
            group_dict[i] = tmp

        feature_info["chi2_values"]["dfc"] = dfc
        feature_info["chi2_values"]["gr"] = gr
        feature_info["chi2_values"]["gr0"] = gr0
        feature_info["chi2_values"]["m"] = m
        feature_info["chi2_values"]["nc"] = nc
        return group_dict

    def _get_values(self, feature_info):
        """获取各个参数的值

        :param feature_info: 参数信息
        :return: (,)
        """
        feature = feature_info["feature"]
        max_box = feature_info["chi2_params"]["bins"]
        chi2_threshold = feature_info["chi2_params"]["threshold"]
        ser_chi2_categorical = feature_info["chi2_values"]["ser_chi2"]
        dfc = feature_info["chi2_values"]["dfc"]
        gr = feature_info["chi2_values"]["gr"]
        gr0 = feature_info["chi2_values"]["gr0"]
        m = feature_info["chi2_values"]["m"]
        nc = feature_info["chi2_values"]["nc"]

        return (feature, max_box, chi2_threshold, ser_chi2_categorical, dfc, gr, gr0, m, nc)

    @exec_log("HOST卡方分箱计算")
    def bin_process_host(self, log: Callable = None) -> Dict[str, Any]:
        """HOST卡方分箱

        Args:
            log (Callable): 日志

        Returns:
            Dict[str,Any]: 分箱结果， {'feature':[], }
        """
        logger.info(f"{LOG_PREFIX}(host)卡方分箱开始，发送features_a:{self.hex_features_dict}")
        # 发送features_a
        self.data_transfer["algo_data_transfer"].features_a_event.send_by_nid(
            self.guest_nid, self.hex_features_dict, self.data_transfer["ctx"], self.data_transfer["job_id"], self.data_transfer["curr_nid"])
        # 获取features_info
        features_info = self._get_features_info_and_send_group_dict()
        iter_ = 0
        while features_info:
            iter_ += 1
            log(f"{LOG_PREFIX}HOST方，卡方分箱迭代{iter_}次")
            # 接收finish, min_chi2_index
            feature_finish_dict = self.data_transfer["algo_data_transfer"].finish_event.get(
                self.data_transfer["listener"], self.data_transfer["job_id"], self.guest_nid, str(iter_))
            finish_lst = [feature_dict["finish"] for _, feature_dict in feature_finish_dict.items()]
            if all(finish_lst):
                break
            min_chi2_index_dict = self.data_transfer["algo_data_transfer"].min_chi2_index_event.get(
                self.data_transfer["listener"], self.data_transfer["job_id"], self.guest_nid, str(iter_))
            # 获取update_dict, key_delete
            features_update_dict, features_key_delete = self._get_features_update_dict_and_key_delete(
                features_info, feature_finish_dict, min_chi2_index_dict)
            # 发送update_dict, key_delete
            self.data_transfer["algo_data_transfer"].update_dict_event.send_by_nid(
                self.guest_nid, features_update_dict, self.data_transfer["ctx"], self.data_transfer["job_id"], self.data_transfer["curr_nid"], str(iter_))
            self.data_transfer["algo_data_transfer"].key_delete_event.send_by_nid(
                self.guest_nid, features_key_delete, self.data_transfer["ctx"], self.data_transfer["job_id"], self.data_transfer["curr_nid"], str(iter_))
        log(f"{LOG_PREFIX}HOST方，完成卡方分箱，共迭代{iter_}次")
        sep_vals = self._get_sep_vals(features_info)
        return self._get_features_dict(sep_vals)

    def _get_sep_vals(self, features_info):
        """获取卡方分箱值sep_vals

        :param features_info: 特征信息
        :return: sep_vals
        """
        sep_vals = {}
        for _, feature_info in features_info.items():
            feature = feature_info["feature"]
            distribution = feature_info["distribution"]
            if distribution == Distribution.CONTINUOUS.value:
                df = feature_info["chi2_values"]["df"]
                sep_vals[feature] = self._get_sep_val(df['sep'])
            else:
                dfc = feature_info["chi2_values"]["dfc"]
                if dfc[feature].dtype == "object":
                    sep_vals[feature] = dfc[feature].tolist()
                else:
                    sep_vals[feature] = dfc[feature].apply(str).tolist()
        return sep_vals

    def _get_sep_val(self, ser):
        """获取df['sep']新值

        :param ser: df['sep']
        :return: [-inf, sep.left, inf]
        """
        sep_val = []
        for i, sep in enumerate(ser):
            if i == 0:
                sep_val.append(-np.inf)
            else:
                sep_val.append(sep.left)
        sep_val.append(np.inf)
        return sep_val

    def _get_features_update_dict_and_key_delete(self, features_info, feature_finish_dict, min_chi2_index_dict):
        """计算卡方update_dict, key_delete

        :param features_info: 特征信息
        :param feature_finish_dict: 特征是否计算结束，dict
        :param min_chi2_index_dict: 卡方索引，dict
        :return: update_dict, key_delete
        """
        features_update_dict = {}
        features_key_delete = {}
        if self.parallel_info.get("parallel"):
            features_update_dict, features_key_delete = self._update_dict_and_key_delete_parallel(
                features_info, min_chi2_index_dict, feature_finish_dict)
        else:
            for hex_feature, feature_info in features_info.items():
                update_dict = None
                key_delete = None
                finish = feature_finish_dict[hex_feature]["finish"]
                if finish == False:
                    min_chi2_index = min_chi2_index_dict[hex_feature]["min_chi2_index"]
                    update_dict, key_delete = _get_update_dict_and_key_delete(feature_info, min_chi2_index)
                features_update_dict[hex_feature] = update_dict
                features_key_delete[hex_feature] = key_delete
        return (features_update_dict, features_key_delete)

    def _update_dict_and_key_delete_parallel(self, features_info, min_chi2_index_dict, feature_finish_dict):
        """并行获取卡方dict, key_delete, 并行输入数据准备

        :param features_info: 特征信息
        :param min_chi2_index_dict: 卡方最小index
        :param feature_finish_dict: 结束标志
        :return: (features_update_dict, features_key_delete)
        """
        features_info_copy = copy.deepcopy(features_info)
        n_parallel = self.parallel_info["n_parallel"]
        features_lst = self.parallel_info["features_lst"]
        info_parallel_lst = []
        for features_ in features_lst:
            features_info_tmp = {feature.encode(
                "utf-8").hex(): features_info_copy[feature.encode("utf-8").hex()] for feature in features_}
            features_min_chi2_index_tmp = {feature.encode(
                "utf-8").hex(): min_chi2_index_dict[feature.encode("utf-8").hex()] for feature in features_}
            features_finish_tmp = {feature.encode(
                "utf-8").hex(): feature_finish_dict[feature.encode("utf-8").hex()] for feature in features_}
            info_parallel_lst.append({"features_info": features_info_tmp,
                                      "features_min_chi2_index": features_min_chi2_index_tmp,
                                      "features_finish": features_finish_tmp})

        features_info_p = {}
        update_dict_p = {}
        key_delete_p = {}
        n_jobs = 1 if n_parallel == 0 else n_parallel
        results = Parallel(n_jobs=n_jobs)(delayed(_get_dict_and_key_delete_parallel)(
            info_parallel, features_info_p, update_dict_p, key_delete_p) for info_parallel in info_parallel_lst)

        # 并行结果转换
        features_update_dict = {}
        features_key_delete = {}
        features_info_new = {}
        for (features_info_, update_dict, key_delete) in results:
            features_info_new.update(features_info_)
            features_update_dict.update(update_dict)
            features_key_delete.update(key_delete)

        # 更新features_info
        features_info.update(features_info_new)
        return (features_update_dict, features_key_delete)

    def _get_features_info_and_send_group_dict(self) -> Dict[str, Any]:
        """获取特征信息，发送卡方group_dict"""
        features_info = {}
        features_group_dict = {}
        if self.parallel_info.get("parallel"):
            features_info, features_group_dict = self._update_features_info_parallel()
        else:
            for hex_feature, feature_info in self.hex_features_dict.items():
                group_dict = _get_group_dict(self.df, self.label, feature_info)
                features_group_dict[hex_feature] = group_dict
                features_info[hex_feature] = feature_info

        # 发送features_group_dict
        self.data_transfer["algo_data_transfer"].group_dict_event.send_by_nid(
            self.guest_nid, features_group_dict, self.data_transfer["ctx"], self.data_transfer["job_id"], self.data_transfer["curr_nid"])

        return features_info

    def _update_features_info_parallel(self) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """并行更新特征信息

        :return: (features_info, features_group_dict)
        """
        n_parallel = self.parallel_info["n_parallel"]
        features_lst = self.parallel_info["features_lst"]
        df_parallel_lst = []
        for feature in features_lst:
            df_parallel_lst.append(self.df.loc[:, feature + [self.label]])

        info_tmp = {}
        group_dict_tmp = {}
        n_jobs = 1 if n_parallel == 0 else n_parallel
        results = Parallel(n_jobs=n_jobs)(delayed(_get_features_info_parallel)(self.label, self.hex_features_dict, df_parallel, info_tmp, group_dict_tmp)
                                          for df_parallel in df_parallel_lst)
        # 并行结果转换
        features_info = {}
        features_group_dict = {}
        for (info, group_dict) in results:
            features_info.update(info)
            features_group_dict.update(group_dict)
        return (features_info, features_group_dict)

    def _get_features_dict(self,
                           sep_vals: Dict[str, Any]) -> Dict[str, Any]:
        """分组，获取特征字典

        Args:
            sep_vals (Dict[str, Any]): 特征计算后的分箱参数值，{"feature": Any}

        Returns:
            Dict[str, Any]: 分箱结果，{"feature": {"success": 1, "msg": "", "result": group_result}...}
        """
        features_dict = {}
        for feature, distribution in self.features.items():
            df = self.df.loc[:, [feature, self.label]]
            param = sep_vals[feature]
            if distribution == Distribution.CONTINUOUS.value:
                features_dict[feature] = get_con_feature_bin(df, self.label, feature, param)
            else:
                features_dict[feature] = get_cat_feature_bin(df, self.label, feature, param)
        return features_dict

    @staticmethod
    @exec_log("GUEST协助HOST卡方分箱计算")
    def bin_process_assist_host(log: Callable,
                                flnodes_tuple: Dict[str, str],
                                priv: Any,
                                data_transfer: Dict[str, Any]):
        """GUEST协助HOST进行卡方分箱计算

        Args:
            log (Callable): 日志
            flnodes_tuple (Dict[str, str]): 其他节点信息，{nid: nid}
            priv (Any): 私钥
            data_transfer (Dict[str, Any]): 通信集合
        """
        nodes_features_dict, nodes_features_group_dict = ChimergeBin.__get_flnodes_features_and_chi2(
            flnodes_tuple, data_transfer)
        nodes_features_info = ChimergeBin.__transform_chi2_info(
            flnodes_tuple, nodes_features_dict, nodes_features_group_dict, priv)
        finish_lst = [feature_dict["finish"] for _, features_info in nodes_features_info.items()
                      for _, feature_dict in features_info.items()]
        iter_ = 0
        while not all(finish_lst):
            iter_ += 1
            log(f"{LOG_PREFIX}GUEST方协助HOST方，卡方分箱，第{iter_}次迭代")
            # 更新特征字典信息
            ChimergeBin.__update_nodes_features_dict(nodes_features_info)

            # 发送finish, min_chi2_index
            for nid, features_info in nodes_features_info.items():
                flnode_nid = nid
                finish_dict = {hex_feature: {"finish": feature_info["finish"]}
                               for hex_feature, feature_info in features_info.items()}
                data_transfer["algo_data_transfer"].finish_event.send_by_nid(flnode_nid, finish_dict,
                                                                             data_transfer["ctx"],
                                                                             data_transfer["job_id"],
                                                                             data_transfer["curr_nid"], str(iter_))

                node_finish_lst = [feature_info["finish"] for _, feature_info in features_info.items()]
                if all(node_finish_lst):
                    continue
                min_chi2_index_dict = {
                    hex_feature: {"min_chi2_index": feature_info["chi2_values"]["min_chi2_index"]} for
                    hex_feature, feature_info in features_info.items()}
                data_transfer["algo_data_transfer"].min_chi2_index_event.send_by_nid(flnode_nid, min_chi2_index_dict,
                                                                                     data_transfer["ctx"],
                                                                                     data_transfer["job_id"],
                                                                                     data_transfer["curr_nid"],
                                                                                     str(iter_))

            flnode_info_dict = ChimergeBin.__get_flnode_info_dict(nodes_features_info, iter_, data_transfer)
            ChimergeBin.__update_feature_dict(nodes_features_info, flnode_info_dict, priv)
            finish_lst = [feature_info["finish"] for _, features_info in nodes_features_info.items()
                          for _, feature_info in features_info.items()]

        log(f"{LOG_PREFIX}GUEST方协助HOST方，卡方分箱完成，共迭代{iter_}次")

    @staticmethod
    @exec_time
    def __get_flnodes_features_and_chi2(flnodes_tuple: Dict[str, str],
                                        data_transfer: Dict[str, Any]
                                        ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """获取其他节点特征，卡方信息

        Args:
            flnodes_tuple (Dict[str, str]): 其他节点信息，{nid: nid}
            data_transfer (Dict[str, Any]): 通信集合

        Returns: 
            nodes_features_dict, nodes_features_group_dict
        """
        nodes_features_dict = {}
        nodes_features_group_dict = {}
        for _, flnode_nid in flnodes_tuple.items():
            features_ = data_transfer["algo_data_transfer"].features_a_event.get(
                data_transfer["listener"], data_transfer["job_id"], flnode_nid)

            features_group_dict = data_transfer["algo_data_transfer"].group_dict_event.get(
                data_transfer["listener"], data_transfer["job_id"], flnode_nid)
            nodes_features_dict[flnode_nid] = features_
            nodes_features_group_dict[flnode_nid] = features_group_dict
        return (nodes_features_dict, nodes_features_group_dict)

    @staticmethod
    @exec_except
    def __update_nodes_features_dict(nodes_features_info: Dict[str, Any]) -> None:
        """更新节点特征的特征字典

        Args:
            nodes_features_info (Dict[str, Any]): 节点特征信息
        """
        for _, features_info in nodes_features_info.items():
            for _, feature_info in features_info.items():
                ser_chi2 = feature_info["chi2_values"]["ser_chi2"]
                if ser_chi2 is None:
                    finish = True
                    min_chi2_index = None
                else:
                    min_chi2, min_chi2_index = ChimergeBin.__get_min_chi2(ser_chi2)
                    finish = _finish_check(feature_info, min_chi2, ser_chi2)
                feature_info["chi2_values"]["min_chi2_index"] = min_chi2_index
                feature_info["finish"] = finish

    @staticmethod
    def __get_flnode_info_dict(nodes_features_info: Dict[str, Any],
                               iter_: int,
                               data_transfer: Dict[str, Any]) -> Dict[str, Any]:
        """获取其他节点的update_dict, key_delete

        Args:
            nodes_features_info (Dict[str, Any]): 节点特征信息
            iter_ (int): 迭代次数
            data_transfer (Dict[str, Any]): 通信集合

        Returns:
            Dict[str, Any]: flnode_info_dict
        """
        flnode_info_dict = {}
        for nid, features_info in nodes_features_info.items():
            flnode_nid = nid
            flnode_info_dict[flnode_nid] = {"update_dict": None, "key_delete": None}
            node_finish_lst = [feature_info["finish"] for _, feature_info in features_info.items()]
            if all(node_finish_lst):
                continue

            # 接收update_dict, key_delete
            update_dict = data_transfer["algo_data_transfer"].update_dict_event.get(
                data_transfer["listener"], data_transfer["job_id"], flnode_nid, str(iter_))
            key_delete = data_transfer["algo_data_transfer"].key_delete_event.get(
                data_transfer["listener"], data_transfer["job_id"], flnode_nid, str(iter_))

            flnode_info_dict[flnode_nid] = {"update_dict": update_dict, "key_delete": key_delete}
        return flnode_info_dict

    @staticmethod
    def __update_feature_dict(nodes_features_info: Dict[str, Any],
                              flnode_info_dict: Dict[str, Any],
                              priv: Any) -> None:
        """更新feature_dict

        Args:
            nodes_features_info (Dict[str, Any]): 节点特征信息
            flnode_info_dict (Dict[str, Any]): 其他节点的update_dict和key_delete值
            priv (Any): 私钥
        """
        for nid, features_info in nodes_features_info.items():
            features_key_delete = flnode_info_dict[nid]["key_delete"]
            features_update_dict = flnode_info_dict[nid]["update_dict"]
            for hex_feature, feature_info in features_info.items():
                finish = feature_info["finish"]
                if finish == False:
                    ser_chi2 = feature_info["chi2_values"]["ser_chi2"]
                    key_delete = features_key_delete[hex_feature]
                    update_dict = features_update_dict[hex_feature]
                    feature_info["chi2_values"]["ser_chi2"] = ChimergeBin.__update_ser_chi2(
                        ser_chi2, key_delete, update_dict, priv)

    @staticmethod
    def __update_ser_chi2(ser_chi2: pd.Series,
                          key_delete: List,
                          update_dict: Dict[str, Any],
                          priv: Any) -> pd.Series:
        """更新存储卡方值的series

        Args:
            ser_chi2 (pd.Series): 卡方值
            key_delete (List): 需要先删除不适用的部分
            update_dict (Dict[str,Any]): 需要解密的更新的部分
            priv (Any): 密钥

        Returns:
            pd.Series: 新的卡方值
        """
        ser_chi2.drop(index=key_delete, inplace=True)
        decrypted_update = _decrypt_data(update_dict, priv)
        ser_update = _cal_all_chi2(decrypted_update)
        ser_chi2 = pd.concat([ser_chi2, ser_update])
        return ser_chi2

    @staticmethod
    def __get_min_chi2(ser: pd.Series) -> Tuple[Any, Any]:
        """获取卡方最小值及其索引，找到最小卡方及对应的index，如果有多个，选第一个

        Args:
            ser (pd.Series): series

        Raises:
            ValueError: ValueError

        Returns:
            Tuple[int, int]: (ser.min(), ser.idxmin())
        """
        # logger.info(f"===>>最小卡方，get_min_chi2, ser:\n{ser}")
        if len(ser) == 0:
            raise ValueError("卡方阈值太大")
        return (ser.min(), ser.idxmin())

    @staticmethod
    def __transform_chi2_info(flnodes_tuple: Dict[str, str],
                              nodes_features_dict: Dict[str, Any],
                              nodes_features_group_dict: Dict[str, Any],
                              priv: Any) -> Dict[str, Any]:
        """根据不同节点不同特征的信息计算出卡方信息

        Args:
            flnodes_tuple (Dict[str, str]): 其他节点
            nodes_features_dict (Dict[str, Any]): 节点特征字典
            nodes_features_group_dict (Dict[str, Any]): 节点特征group_dict值
            priv (Any): 私钥

        Returns:
            Dict[str, Any]: nodes_features_info
                            {n1:{"hex_feature":{"feature":"", "distribution":1, "finish":False, "chi2_params": {}, "chi2_values": {}}}}
        """
        nodes_features_info = {}
        for _, flnode_nid in flnodes_tuple.items():
            features_ = nodes_features_dict[flnode_nid]
            features_group_dict = nodes_features_group_dict[flnode_nid]

            features_info = {}
            for hex_feature, feature_info in features_.items():
                feature_info["finish"] = False
                feature_info["chi2_values"]["min_chi2_index"] = None

                group_dict = features_group_dict[hex_feature]
                decrypted_dict = _decrypt_data(group_dict, priv)
                ser_chi2 = _cal_all_chi2(decrypted_dict)
                feature_info["chi2_values"]["ser_chi2"] = ser_chi2
                features_info[hex_feature] = feature_info
            nodes_features_info[flnode_nid] = features_info
        return nodes_features_info

    def bin_process_merging(self,
                            features_dict: Dict[str, Any]) -> Dict[str, Any]:
        """根据分箱结果进行分箱合并

        Args:
            features_dict (Dict[str, Any]): 分箱结果

        Returns:
            Dict[str, Any]: {"feature": {"success": 1/0, "msg": msg, "result": df}}
        """
        return self.tool.bins_merging(self.static_bin_type(), self.features, features_dict, self.con_params["min_samples"], self.cat_params["min_samples"])

    @staticmethod
    def static_bin_type() -> str:
        return BinType.CHIMERGE_BIN.name


def _trans_df(df: pd.DataFrame,
              priv: Any) -> pd.DataFrame:
    """解密，获取df[["val_1", "val_0"]]

    Args:
        df (pd.DataFrame): dataframe
        priv (Any): 私钥

    Returns:
        pd.DataFrame: dataframe
    """
    df_ = df.copy()
    df_.loc[:, "val_1"] = df["val_1"].apply(lambda x: decrypting(x, priv))
    df_.loc[:, "val_0"] = df_.loc[:, "num"] - df_.loc[:, "val_1"]
    return df_.loc[:, ["val_1", "val_0"]]


def _decrypt_data(data: Dict[str, Any],
                  priv: Any) -> Dict[str, Any]:
    """data解密

    Args:
        data (Dict[str, Any]): 待解密数据
        priv (Any): 私钥

    Returns:
        Dict[str, Any]: 解密后的字典
    """
    decrypted_dict = {}
    for k, v in data.items():
        decrypted_dict[k] = _trans_df(v, priv)
    return decrypted_dict


def _cal_chi2(df: pd.DataFrame) -> float:
    """计算单个分组的卡方值
    输入df2行2列，2行是临近的2个组，列名为val_1和val_0分别代表分组中取值为0的数量和取值为1的数量

    Args:
        df (pd.DataFrame): dataframe

    Returns:
        float: chi2 value
    """
    R_N = df.sum(axis=0)
    C_N = df.sum(axis=1)
    N = R_N.sum()
    chi2_val = 0
    for i in df.index:
        for j in range(len(df.columns)):
            E = R_N[i] * C_N[j] / N
            if E == 0:
                tmp_chi2 = 0
            else:
                tmp_chi2 = (df.iloc[i, j] - E) ** 2 / E
            chi2_val += tmp_chi2
    return chi2_val


def _cal_all_chi2(group_dict: Dict[Any, Any]) -> Any:
    """计算所有分组的卡方值

    Args:
        group_dict (Dict[int, Any]): 分组字典，{0:idx, 1:idx2, ...}

    Returns:
        Any: None or series(chi2_val, index=keys)
    """
    if len(group_dict) < 1:
        return None

    chi2_val = []
    keys = []
    for k, v in group_dict.items():
        tmp_chi2 = _cal_chi2(v)
        chi2_val.append(tmp_chi2)
        keys.append(k)
    return pd.Series(chi2_val, index=keys)


def _threshold_check(threshold: Any,
                     min_chi2: Any) -> bool:
    """最小卡方值是否大于卡方阈值

    Args:
        threshold (Any): 卡方阈值
        min_chi2 (Any): 最小卡方值

    Returns:
        bool: status
    """
    return threshold <= min_chi2


def _bins_check(curr_bin: Any,
                max_bins: int) -> bool:
    """bins check status

    Args:
        curr_bin (Any): 当前箱
        max_bins (int): 最大箱数

    Returns:
        bool: status
    """
    return len(curr_bin) < max_bins


def _update_enums_lst(enums_lst, left, right):
    """更新enums_lst

    :param enums_lst: []
    :param left: dfc.loc[to_merge[0], feature]
    :param right: dfc.loc[to_merge[1], feature]
    """
    if isinstance(left, str):
        enums_lst.append(left)
    else:
        enums_lst += left
    if isinstance(right, str):
        enums_lst.append(right)
    else:
        enums_lst += right


def _finish_check(feature_info: Dict[str, Any],
                  min_chi2: float,
                  ser_chi2: pd.Series) -> bool:
    """finish check status

    Args:
        feature_info (Dict[str,Any]): 特征信息
        min_chi2 (float): 最小卡方值
        ser_chi2 (pd.Series): 卡方值

    Returns:
        bool: finish status
    """
    if feature_info["distribution"] == Distribution.DISCRETE.value and ser_chi2.count() <= 1:
        return True

    if _threshold_check(feature_info["chi2_params"]["threshold"], min_chi2) and _bins_check(
            ser_chi2, feature_info["chi2_params"]["bins"]):
        return True
    else:
        return False


def _map_index(df):
    """发给y方时需要打乱顺序，所以需要把原始顺序和打乱后的顺序对应起来

    :param df: dataframe
    :return: {原始值：打乱值}
    """
    list_ori = list(df.index.values)
    list_new = list(np.random.permutation(list_ori))
    dict_index_map = {}
    for i in range(len(list_ori)):
        dict_index_map[list_ori[i]] = list_new[i]
    return dict_index_map


def _first_group_dict(df, d):
    """把所有的分箱都存入一个dict，以分箱df为dict的值，打乱后的索引为dict的key

    :param df: df
    :param d: index_dic={原始值：打乱值}
    :return: {}
    """
    group_dict = {}
    # 每一行和它下面的一行合并，最后一行没有，所以-1
    for i in range(len(df.index) - 1):
        group_dict[d[i]] = df.loc[i:i + 1, ["num", "val_1"]].reset_index().drop(columns="index")
    return group_dict


def _get_con_group_dict(df, label, feature_info):
    """获取连续特征的卡方group_dict

    :param df: dataframe
    :param label: 标签
    :param feature_info: 特征卡方相关信息
    :return: 卡方group_dict
    """
    feature = feature_info["feature"]

    df0 = df.loc[:, [feature, label]]
    # 初始先等频拆分成100箱，然后再逐层合并
    df0['sep'] = pd.qcut(df0[feature], 100, duplicates='drop')
    logger.info(f"===>>(host)根据同态密文进行分箱qcut之后:\n{df0}")
    df = df0.groupby('sep', sort=True)[label].agg([("num", "count"), ("val_1", "sum")])
    # 过滤分箱记录数为0的分箱
    df = df[df['num'] > 0]
    df = df.reset_index()
    n = df.shape[0]
    dict_index_map = _map_index(df)
    group_dict = _first_group_dict(df, dict_index_map)

    feature_info["chi2_values"]["df"] = df
    feature_info["chi2_values"]["dict_index_map"] = dict_index_map
    feature_info["chi2_values"]["n"] = n
    return group_dict


def _get_cat_group_dict(df, label, feature_info):
    """获取离散特征的卡方group_dict

    :param df: dataframe
    :param label: 标签
    :param feature_info: 特征卡方相关信息
    :return: 卡方group_dict
    """
    feature = feature_info["feature"]

    df1 = df.loc[:, [feature, label]]
    dfc = df1.groupby(feature)[label].agg([("num", "count"), ("val_1", "sum")])
    dfc.reset_index(inplace=True)
    nc = len(dfc)
    gr0 = list(combinations(dfc.index, 2))
    gr = gr0.copy()
    m = len(gr0)
    group_dict = {}
    for i, idx in enumerate(gr):
        idx = list(idx)
        tmp = dfc.loc[idx, ["num", "val_1"]]
        tmp.index = [0, 1]
        group_dict[i] = tmp

    feature_info["chi2_values"]["dfc"] = dfc
    feature_info["chi2_values"]["gr0"] = gr0
    feature_info["chi2_values"]["nc"] = nc
    feature_info["chi2_values"]["gr"] = gr
    feature_info["chi2_values"]["m"] = m
    return group_dict


def _get_group_dict(df, label, feature_info):
    """获取卡方分箱字典信息group_dict

    :param df: dataframe
    :param label: 标签
    :param feature_info: 特征卡方相关信息
    :return: group_dict, feature_info
    """
    distribution = feature_info["distribution"]
    if distribution == Distribution.CONTINUOUS.value:
        group_dict = _get_con_group_dict(df, label, feature_info)
    else:
        group_dict = _get_cat_group_dict(df, label, feature_info)
    return group_dict


def _get_features_info_parallel(label, features_dict, df_parallel, features_info, features_group_dict):
    """并行获取特征信息

    :param label: 标签
    :param features_dict: 特征字典
    :param df_parallel: 并行dataframe
    :param features_info: 特征信息
    :param features_group_dict: 特征分箱字典
    :return: (features_info, features_group_dict)
    """
    features_ = [x for x in df_parallel.columns if x != label]
    for feature in features_:
        hex_feature = feature.encode("utf-8").hex()
        df = df_parallel[[feature, label]]
        feature_info = features_dict[hex_feature]
        # compute
        group_dict = _get_group_dict(df, label, feature_info)
        # update dict
        features_group_dict[hex_feature] = group_dict
        features_info[hex_feature] = feature_info
    return (features_info, features_group_dict)


def _val_to_key(d, val):
    """当y方返回打乱后的最小卡方索引时，x方需要根据该值找到原始的index

    :param d: 字典
    :param val: 值
    :return: key
    """
    l = [k for k, v in d.items() if v == val]
    return l[0]


def _con_merge(df, dict_index_map, key_y, n):
    """dataframe数据合并

    :param df: dataframe
    :param dict_index_map: {原始值：打乱值}
    :param key_y: min_chi2_index
    :param n: df.shape[0]
    :return: df, dict_index_map, update_dict, key_delete, n
    """
    key_xa = None
    # 将给y方的键对应回来
    key_x = _val_to_key(dict_index_map, key_y)
    # 定位key_x前后的行
    pos = df.index.tolist().index(key_x)
    key_xb = df.index[pos + 1]  # key_xb 就是箱体合并前key_x在df中的下一行
    if key_x != df.index[0]:
        key_xa = df.index[pos - 1]  # key_xa 是key_x在df中的上一行
    # 合并后一行
    df.loc[key_x, "num"] = df.loc[key_x, "num"] + df.loc[key_xb, "num"]
    df.loc[key_x, "val_1"] = df.loc[key_x, "val_1"] + df.loc[key_xb, "val_1"]
    df = df.drop(index=key_xb, axis=0)
    # 合并行及前后的键需要交给y方删除
    if key_x == df.index[0]:  # 如果key_x就是第一行，那么不涉及前面的数据
        key_delete = [key_y, dict_index_map[key_xb]]
    elif key_x == df.index[-1]:  # 如果key_x是最后一箱，那么不涉及后面的数据
        key_delete = [key_y, dict_index_map[key_xa]]
    else:
        key_delete = [key_y, dict_index_map[key_xa], dict_index_map[key_xb]]
    # dict_index_map需要更新，另有部分需要重新计算卡方
    update_dict = {}
    if key_x != df.index[-1]:
        dict_index_map[key_x] = n
        n += 1
        update_dict[dict_index_map[key_x]] = df.iloc[[pos, pos + 1], [1, 2]].reset_index().drop(columns="index")
    # 如果key_x不是第一行，那key_x前一行也需要更新
    if key_x != df.index[0]:
        dict_index_map[key_xa] = n
        update_dict[dict_index_map[key_xa]] = df.iloc[[pos - 1, pos], [1, 2]].reset_index().drop(columns="index")
        n += 1
    return (df, dict_index_map, update_dict, key_delete, n)


def _cat_merge(values_dict, min_chi2_index):
    """离散特征

    :param feature: 特征
    :param min_chi2_index: min_chi2_index
    :return: (gr0, dfc, nc, gr, m, update_dict_categorical, key_delete)
    """
    feature = values_dict["feature"]
    gr0 = values_dict["gr0"]
    dfc = values_dict["dfc"]
    if dfc[feature].dtype != "object":
        dfc[feature] = dfc[feature].apply(str)
    nc = values_dict["nc"]
    gr = values_dict["gr"]
    m = values_dict["m"]
    to_merge = gr0[min_chi2_index]
    to_merge = list(to_merge)
    combine = pd.DataFrame()  # 合并后的新结果
    enums_lst = list()
    left = dfc.loc[to_merge[0], feature]
    right = dfc.loc[to_merge[1], feature]
    if type(left) == str:
        enums_lst.append(left)
    else:
        enums_lst += left
    if type(right) == str:
        enums_lst.append(right)
    else:
        enums_lst += right
    combine[feature] = [enums_lst]
    combine["num"] = dfc.loc[to_merge[0], "num"] + dfc.loc[to_merge[1], "num"]
    combine["val_1"] = dfc.loc[to_merge[0], "val_1"] + dfc.loc[to_merge[1], "val_1"]
    combine.index = [nc]
    nc = nc + 1
    # 将合并的两列从原始表格中删除
    dfc.drop(index=to_merge, inplace=True)
    # 删除后剩余组合（不需要更新的部分）
    remained_comb = list(combinations(dfc.index, 2))
    delete_comb = list(set(gr) - set(remained_comb))
    key_delete = []
    for i in delete_comb:
        # 需要删除的卡方
        key_delete.append(gr0.index(i))
    # 将合并后的结果并入原始表格
    dfc = pd.concat([dfc, combine], axis=0)
    # 合并后的所有组合
    gr = list(combinations(dfc.index, 2))
    # 需要更新的部分
    to_update = list(set(gr) - set(remained_comb))
    update_dict = {}
    for i, idx in enumerate(to_update):
        idx = list(idx)
        tmp = dfc.loc[idx, ["num", "val_1"]]
        tmp.index = [0, 1]
        update_dict[i + m] = tmp
    gr0.extend(to_update)
    m = len(gr0)
    return (gr0, dfc, nc, gr, m, update_dict, key_delete)


def _get_update_dict_and_key_delete(feature_info, min_chi2_index):
    """获取卡方特征字典update_dict, 需要删除的键key_delete

    :param feature_info: 特征卡方相关信息
    :param min_chi2_index: min_chi2_index
    :return: (update_dict, key_delete)
    """
    if feature_info["distribution"] == Distribution.CONTINUOUS.value:
        df = feature_info["chi2_values"]["df"]
        dict_index_map = feature_info["chi2_values"]["dict_index_map"]
        n = feature_info["chi2_values"]["n"]
        # compute
        df, dict_index_map, update_dict, key_delete, n = _con_merge(df, dict_index_map, min_chi2_index, n)

        feature_info["chi2_values"]["df"] = df
        feature_info["chi2_values"]["dict_index_map"] = dict_index_map
        feature_info["chi2_values"]["n"] = n
    else:
        values_dict = {"feature": feature_info["feature"],
                       "gr0": feature_info["chi2_values"]["gr0"],
                       "dfc": feature_info["chi2_values"]["dfc"],
                       "nc": feature_info["chi2_values"]["nc"],
                       "gr": feature_info["chi2_values"]["gr"],
                       "m": feature_info["chi2_values"]["m"]}
        # compute
        gr0, dfc, nc, gr, m, update_dict, key_delete = _cat_merge(
            values_dict, min_chi2_index)

        feature_info["chi2_values"]["gr0"] = gr0
        feature_info["chi2_values"]["dfc"] = dfc
        feature_info["chi2_values"]["nc"] = nc
        feature_info["chi2_values"]["gr"] = gr
        feature_info["chi2_values"]["m"] = m
    return (update_dict, key_delete)


def _get_dict_and_key_delete_parallel(features_info_parallel, features_info_dict, features_update_dict, features_key_delete):
    """并行获取卡方update_dict, key_delete, 并行逻辑

    :param features_info_parallel: 并行特征信息
    :param features_info_dict: features_info容器
    :param features_update_dict: update_dict容器
    :param features_key_delete: key_delete容器
    :return: (features_info_dict, features_update_dict, features_key_delete)
    """
    features_info = features_info_parallel["features_info"]
    features_finish = features_info_parallel["features_finish"]
    features_min_chi2_index = features_info_parallel["features_min_chi2_index"]

    for hex_feature, feature_info in features_info.items():
        update_dict = None
        key_delete = None

        finish = features_finish[hex_feature]["finish"]
        if finish == False:
            min_chi2_index = features_min_chi2_index[hex_feature]["min_chi2_index"]
            update_dict, key_delete = _get_update_dict_and_key_delete(feature_info, min_chi2_index)

        features_info_dict[hex_feature] = feature_info
        features_update_dict[hex_feature] = update_dict
        features_key_delete[hex_feature] = key_delete
    return (features_info_dict, features_update_dict, features_key_delete)
