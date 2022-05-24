'''
Author: hexu
Date: 2022-02-20 10:49:18
LastEditTime: 2022-05-17 17:02:45
LastEditors: Hexu
Description: 按列的特征处理
FilePath: /iw-algo-fx/intelliw/functions/feature_process.py
'''
from copy import deepcopy
import json
import numpy as np
import pandas as pd
from sklearn.cluster import KMeans
from intelliw.utils import message
from intelliw.utils.util import default_dump
from collections import Iterable
from intelliw.datasets.datasets import DataSets
from intelliw.config import cfg_parser
from intelliw.config import config as intelliw_core_config
from intelliw.utils.logger import get_logger
from intelliw.utils.global_val import gl


class FeatureProcessException(Exception):
    pass


logger = get_logger()

COl_PREFIX = "col_"

stage_feature_map = {
    "pre-train": "train",
    "post-train": "train",
    "pre-predict": "infer",
    "post-predict": "infer",
    "infer":"infer",
    "train":"train",
}

stage_infer_map = {
    "pre-train": "pre-predict",
    "post-train": "post-predict",
}

# injection_alg_yaml 新的配置注入到旧的配置里
# yaml_path 配置文件位置
# 能到这部key都是存在的，不用担心没有key
def injection_alg_yaml(yaml_path, val, stage, type):
    cfg = cfg_parser.load_single_config(yaml_path)
    value = [
                {
                    "key": "feature_process_param",
                    "desc": "特征处理参数",
                    "name": "特征处理参数",
                    "val": val,
                    "option": {"defaultValue": "", "type": "string"}
                }
            ]
    if type == "algorithm":
        transforms = cfg["AlgorithmInformation"]["algorithm"]["transforms"]
    else:
        transforms = cfg["Model"]["transforms"]
    
    for t in transforms:
        if t["type"] == stage:
            for f in t["functions"]:
                if f["key"] == "feature_process":
                    f["parameters"] = value
                    break
            else:
                t["functions"].append({"key":"feature_process", "parameters":value})
            break
    else:
        transforms.append({"type":stage, "functions":[{"key":"feature_process", "parameters":value}]})
    return cfg


def feature_process(data, config: list, stage: str, _type:str) -> Iterable:    
    """特征工程处理

    Args:
        data (object): 需要处理的数据
        config (list): 特征值配置
        stage (str): 处理类型 pre-train/post-train/pre-predict/post-predict
        _type (str): 数据集类型 验证集/训练集  如果胃验证集应按照推理的方式处理

    Returns:
        Iterable: _description_
    """    
    alg_yaml_file, model_yaml_file = gl.get("alg_yaml_file"), gl.get("model_yaml_file")
    if not config and not alg_yaml_file and not model_yaml_file:
        return data

    logger.info("{} feature process start".format(_type))
    processor_mode = stage_feature_map[stage]
    
    if processor_mode == "infer":
        if "data" not in data:
            raise KeyError("如果使用特征处理功能, 推理请求的输入必须放在data参数下")
        infer_data = data["data"]
        df = pd.DataFrame(infer_data)
        _,col = df.shape
        if len(config) != col:
            raise KeyError(f"输入特征数量不正确, 输入特征数量{col}, 模型需要特征数量{len(config)}") 
        fp = FeatureProcessor(config, processor_mode)
        result, _, _, _ = fp.do_process(df,fit=True if _type == "train_set" else False)
        data["data"] = result.values.tolist()
        data["original_data"] = infer_data
        return data
    else:
        # 获取所有数据
        alldata = data
        result = alldata.get("result")
        # 对数据进行处理
        if intelliw_core_config.SOURCE_TYPE != 4 and result:
            column_meta = [col.get("column_code", col["column_name"]) for col in config]
            df = pd.DataFrame(result)

            # 修改列名（如果用户修改了用新的， 没修改保持不变）
            col_code_map = {}
            df.rename(columns=col_code_map, inplace=True) 
            
            # 特征处理可能会修改目标列的属性，所以需要先保存起来
            target_metadata = gl.get("target_metadata")
            target_data = None
            if target_metadata and len(target_metadata) > 0:
                target_cols = [m['target_col'] for m in target_metadata]
                target_data = df.iloc[:, target_cols]
                # 检查目标列是否要做特征工程，如果是删除目标列特征配置
                for idx, c in enumerate(deepcopy(config)):
                    if c["col"] in target_cols:
                        config.pop(idx)
                logger.info("target data save to memory")
            
            fp = FeatureProcessor(config, processor_mode)
            result, category_cols, new_config, col_map_df = fp.do_process(df,True if _type == "train_set" else False)
           

            # 将目标列加入数据
            if target_data is not None:
                target_names = [m['target_name'] for m in target_metadata]
                target_data.columns = target_names
                result = pd.concat([result, target_data], axis=1)
                column_meta.extend(target_names)
                target_cols = [{"col":result.columns.get_loc(name), "column_name":name} for name in target_names]
                gl.set("target_cols", target_cols)
                gl.set("final_target_col", target_cols[-1]["col"])  # TODO 暂时兼容后面删除
                logger.info("set new target data and final target col add to param")
            
            # 原始列名
            alldata["meta"] = [{'code': i} for i in result.columns.tolist()]
            alldata["result"] = result.values.tolist()

            gl.set_dict({"category_cols":category_cols, "column_relation_df":col_map_df, "column_meta":column_meta})
            logger.info("{} feature process end".format(_type))
        else:
            return data
        
        # 如果是训练需要写入配置
        if _type == "train_set":
            logger.info("injection yaml start")
            gl.get('feature_process')[stage] = new_config
            new_config = json.dumps(new_config,ensure_ascii=False, default=default_dump)
            if not intelliw_core_config.is_server_mode():
                # 本地测试需要反写入配置文件
                model_yaml = injection_alg_yaml(model_yaml_file, new_config, stage_infer_map[stage], "model")
                cfg_parser.dump_config(model_yaml, model_yaml_file)
                alg_yaml = injection_alg_yaml(alg_yaml_file, new_config, stage_infer_map[stage], "algorithm")
                cfg_parser.dump_config(alg_yaml, alg_yaml_file)
            elif gl.get('reporter'):
                # 线上的上报到AI工作坊
                reporter_info = {"modelInstanceId": intelliw_core_config.INSTANCE_ID,
                                "tenantId": intelliw_core_config.TENANT_ID,
                                "valuationResult": {stage_infer_map[stage]:new_config}}
                gl.get('reporter').report(message.CommonResponse(200, 'feature_config', 'feature_config_upload', reporter_info))
            logger.info("injection yaml end")
        return alldata

class FeatureProcessor:
    def __init__(self, config_list, mode):
        self.config_list = config_list
        self.mode = mode       # train or infer
        self.l_Features = []
        self.col_names = []
        self.col_nums = []
        self.col_map_df = {'origin_num': [], 'origin_name': [], 'final_num': [], 'final_name': []}

        if self.mode == 'train':
            for col_config in config_list:
                idx = col_config['col']
                col_name = col_config.get("column_code", col_config["column_name"])
                self.col_names.append(col_name)
                self.col_nums.append(idx)
                if col_config['type'] in ['int', 'float', 'NUMBER']:
                    feat = NumericFeature(idx, col_config, self.mode)
                elif col_config['type'] in ['string', 'category', 'STRING', 'CATEGORY']:
                    feat = CategoryFeature(idx, col_config, self.mode)
                else:
                    assert False
                self.l_Features.append(feat)

        elif self.mode == 'infer':
            for idx, col_config in enumerate(config_list):
                col_name = col_config.get("column_code", col_config["column_name"])
                self.col_names.append(col_name)
                self.col_nums.append(idx)
                if col_config['type'] in ['int', 'float', 'NUMBER']:
                    feat = NumericFeature(idx, col_config, self.mode)
                elif col_config['type'] in ['string', 'category', 'STRING', 'CATEGORY']:
                    feat = CategoryFeature(idx, col_config, self.mode)
                else:
                    assert False
                self.l_Features.append(feat)


    def do_process(self, data_frame, fit):
        '''
        :param data_frame:
        :return: when self.mode == 'train', processor will fit params with input data, if you just want to do data
                 process without change params, use set_mode('infer') before do_process!

                 df: the output dataframe transformed from data_frame.

                 category_cols: the col_nums of columns which are in category type.

                 config_list: the processing methods used in missing check,miss repairing, outlier check, outlier
                              repairing for each column.

                 col_map_df: the map between the input columns and output columns,ie.:

                                        origin_num origin_name  final_num final_name
                                0           0          id          0          0
                                1           1        name          1          1
                                2           2        math          2          2
                                3           3       level          3          3
                                4           5        ABCD          4        5_0
                                5           5        ABCD          5        5_1
                                6           5        ABCD          6        5_2
                                7           5        ABCD          7        5_3
                                8           5        ABCD          8        5_4
                                9           6        rand          9          6
                            Warning: if column is droped, it will not exist in col_map_df!
        '''

        df = pd.DataFrame()
        self.category_cols = []
        self.col_map_df = {'origin_num': [], 'origin_name': [], 'final_num': [], 'final_name': []}

        if self.mode == 'train':
            if fit:
                self.__set_fit(True)
            else:
                self.__set_fit(False)
        else:
            self.__set_fit(False)

        for i, feat in enumerate(self.l_Features):
            try:
                col_num = df.shape[1]
                tmp_frame, res_params = feat.do_process(data_frame)
                shape = tmp_frame.shape
                if len(shape) > 1:
                    if shape[1] > 0:  # shape[1]为0 时，则该列可能被drop掉了
                        self.col_map_df['origin_num'].extend([self.col_nums[i]] * shape[1])
                        self.col_map_df['final_num'].extend(range(col_num, col_num + shape[1]))
                        self.col_map_df['origin_name'].extend([self.col_names[i]] * shape[1])
                        self.col_map_df['final_name'].extend(tmp_frame.columns)
                else:
                    self.col_map_df['origin_num'].append(self.col_nums[i])
                    self.col_map_df['final_num'].append(col_num)
                    self.col_map_df['origin_name'].append(self.col_names[i])
                    self.col_map_df['final_name'].extend(tmp_frame.columns)

                if isinstance(feat, CategoryFeature):
                    if len(shape) > 1:
                        self.category_cols.extend(range(col_num, col_num + shape[1]))
                    else:
                        self.category_cols.append(col_num)
                
                cols = list(df.columns)
                cols.extend(tmp_frame.columns)
                df = pd.concat([df, tmp_frame], axis=1)
                df.columns = cols
                
                if fit and self.mode == 'train':
                    self.config_list[i]['func'] = res_params
            except Exception as e:
                raise Exception(f"errmsg:{e}, origin_col_num:{feat.index}, final_num:{col_num}, order of the column:{i}")

        self.__set_fit(False)
        self.col_map_df = pd.DataFrame(self.col_map_df)
        return df, self.category_cols, self.config_list, self.col_map_df


    def __set_fit(self, fit):
        if fit:
            for feat in self.l_Features:
                feat.mode = 'train'
        else:
            for feat in self.l_Features:
                feat.mode = 'infer'

class Feature:
    def __init__(self, index, config, mode, **kwargs):
        '''
        :param index:
        :param config:
        :param mode:
        :param auto_process: when mode == 'train' and auto_process == True the recommended func will be used, and params
                             will write back to the feature_engineer_config!
        :param auto_check_repair: when mode == 'train' and auto_check_repair == True, the recommended check_and_repair
                             method will be used, and params will write back to the feature_engineer_config!
        '''
        self.index = index
        self.mode = mode

        self.check_repair_config = config['check_repair']
        self.feature_engineer_config = config['func']
        self.fe_name2func = {}
        self.auto_check_repair = True if config.get('check_repair_auto', '0') == '1' else False
        self.auto_process = True if config.get('func_auto', '0') == '1' else False

    def do_process(self, data_frame):
        pass


class NumericFeature(Feature):
    def __init__(self, index, config, mode, **kwargs):
        super(NumericFeature, self).__init__(index, config, mode, **kwargs)
        self.fe_name2func = {'bucket': bucket,
                             'min_max_scale': min_max_scale,
                             'standard_scale': standard_scale,
                             'log_transform': log_transform,
                             'quantile_transform': quantile_transform,
                             'square': square,
                             'translation': translation,
                             'robust_scale': robust_scale,
                             'drop': drop,
                             'interval_bucket': interval_bucket,
                             'kmeans_bucket': kmeans_bucket,
                             'max_abs_scale':max_abs_scale
                             }


    def recommend_miss_repair(self, feat_df):
        if (feat_df==feat_df.mode()[0]).sum()/len(feat_df) >= 0.75:
            return '4'
        if feat_df.std()/feat_df.mean() <= 1:
            return '1'
        return '5'

    def recommend_outlier_check(self, feat_df):
        mean = feat_df.mean()
        std = feat_df.std()
        low_sigma = mean - 3 * std
        high_sigma = mean + 3 * std
        count_sigma = len(feat_df[feat_df < low_sigma]) + len(feat_df[feat_df > high_sigma])

        low_boxplot = feat_df.quantile(0.25) - 1.5 * (feat_df.quantile(0.75) - feat_df.quantile(0.25))
        high_boxplot = feat_df.quantile(0.75) + 1.5 * (feat_df.quantile(0.75) - feat_df.quantile(0.25))
        count_boxplot = len(feat_df[feat_df < low_boxplot]) + len(feat_df[feat_df > high_boxplot])

        if count_boxplot/len(feat_df) > 0.1 and count_sigma/len(feat_df) > 0.1:
            self.check_repair_config['outlier_check'] = '3'
            return 0, 0
        if count_sigma < count_boxplot:
            self.check_repair_config['outlier_check'] = '1'
            return low_sigma, high_sigma
        self.check_repair_config['outlier_check'] = '2'
        return low_boxplot, high_boxplot

    def recommend_outlier_repair(self, feat_df, low, high):
        if len(feat_df) < 1000 or (low == 0 and high == 0):
            return '3'
        return '1'

    def recommend_process(self, feat_df, low, high):
        # kurt = feat_df.kurt()
        coeff = feat_df.std()/feat_df.mean()
        skew = feat_df.skew()

        if coeff >= 5 and skew > 0:
            return [{'name': 'translation', 'params': {}},
                    {'name': 'log_transform', 'params': {}}]
        # if prop of outliers > 0.1
        if low == 0 and high == 0:
            return [{'name': 'robust_scale', 'params': {}}]
        # if skew == 0 or kurt < 5
        return [{'name': 'min_max_scale', 'params': {}}]

    def do_process(self, data_frame):
        feat_df = data_frame[data_frame.columns[self.index]]

        # check and repair
        if self.mode == 'train':
            # missing repair
            feat_df.replace([np.inf, -np.inf, 'None', 'null', '', ' '], np.nan, inplace=True)
            feat_df = feat_df.astype(float)
            if self.auto_check_repair:
                self.check_repair_config['miss_repair'] = self.recommend_miss_repair(feat_df)

            assert 'miss_repair' in self.check_repair_config
            assert self.check_repair_config['miss_repair'] in ['1', '2', '3', '4', '5']
            if self.check_repair_config['miss_repair'] == '1':
                feat_df = feat_df.fillna(feat_df.mean())
            elif self.check_repair_config['miss_repair'] == '2':
                feat_df = feat_df.fillna(0)
            elif self.check_repair_config['miss_repair'] == '3':
                feat_df = feat_df.fillna(feat_df.quantile(0.5))
            elif self.check_repair_config['miss_repair'] == '4':
                feat_df = feat_df.fillna(feat_df.mode()[0])

            # if feature has the same value, drop it
            if feat_df.nunique() == 1 and self.auto_process:
                self.feature_engineer_config = [{'name': 'drop', 'params': {}}]
                return pd.DataFrame(), self.feature_engineer_config

            # outlier check
            if self.auto_check_repair:
                low, high = self.recommend_outlier_check(feat_df)
            else:
                assert 'outlier_check' in self.check_repair_config
                assert self.check_repair_config['outlier_check'] in ['1', '2', '3']
                low, high = 0, 0
                # 3 西格玛
                if self.check_repair_config['outlier_check'] == '1':
                    mean = feat_df.mean()
                    std = feat_df.std()
                    low = mean - 3 * std
                    high = mean + 3 * std
                elif self.check_repair_config['outlier_check'] == '2':
                    low = feat_df.quantile(0.25) - 1.5 * (feat_df.quantile(0.75) - feat_df.quantile(0.25))
                    high = feat_df.quantile(0.75) + 1.5 * (feat_df.quantile(0.75) - feat_df.quantile(0.25))

            # outlier repair
            if self.auto_check_repair:
                self.check_repair_config['outlier_repair'] = self.recommend_outlier_repair(feat_df, low, high)

            assert 'outlier_repair' in self.check_repair_config
            assert self.check_repair_config['outlier_repair'] in ['1', '2', '3']
            if self.check_repair_config['outlier_repair'] == '1':
                feat_df[feat_df < low] = low
                feat_df[feat_df > high] = high
            elif self.check_repair_config['outlier_repair'] == '2':
                feat_df[feat_df < low] = np.nan
                feat_df[feat_df > high] = np.nan

            if self.auto_process:
                self.feature_engineer_config = self.recommend_process(feat_df, low, high)

        else:
            feat_df = feat_df.astype(float)

        # feature engineering
        for func in self.feature_engineer_config:
            feat_df, params = self.fe_name2func[func['name']](func['params'], feat_df, self.mode)
            if self.mode == 'train':
                func['params'] = params

        cols = []
        if len(feat_df.shape) == 1:
            cols = [f'{self.index}_0']

        elif len(feat_df.shape) == 2:
            for i in range(feat_df.shape[1]):
                cols.append(f'{self.index}_{i}')

        feat_df.columns = cols
        return feat_df, self.feature_engineer_config

class CategoryFeature(Feature):
    def __init__(self, index, config, mode, **kwargs):
        super(CategoryFeature, self).__init__(index, config, mode, **kwargs)

        self.fe_name2func = {'one_hot': one_hot,
                             'ordinal': ordinal,
                             'drop': drop,
                             'hash': hash_feature
                             }

    def recommend_miss_repair(self, feat_df):
        if (feat_df==feat_df.mode()[0]).sum()/len(feat_df) >= 0.75:
            return '4'
        return '5'

    def recommend_process(self, feat_df):
        if feat_df.nunique() > len(feat_df) * 0.9:
            return [{'name': 'hash', 'params': {}}]
        if feat_df.nunique() <= 100:
            return [{'name': 'one_hot', 'params': {}}]
        return [{'name': 'ordinal', 'params': {}}]

    def do_process(self, data_frame):
        feat_df = data_frame[data_frame.columns[self.index]]
        # check and repair
        if self.mode == 'train':
            if self.auto_check_repair:
                self.check_repair_config['miss_repair'] = self.recommend_miss_repair(feat_df)
            # missing repair
            assert 'miss_repair' in self.check_repair_config
            assert self.check_repair_config['miss_repair'] in ['4', '5']
            if self.check_repair_config['miss_repair'] == '4':
                feat_df = feat_df.fillna(feat_df.mode()[0])

            # if feature has the same value, drop it
            if feat_df.nunique() == 1 and self.auto_process:
                self.feature_engineer_config = [{'name': 'drop', 'params': {}}]
                return pd.DataFrame(), self.feature_engineer_config

        if self.mode == 'train' and self.auto_process:
            self.feature_engineer_config = self.recommend_process(feat_df)

        # feature engineering
        for func in self.feature_engineer_config:
            # if func['name'] in self.fe_name2func:
            feat_df, params = self.fe_name2func[func['name']](func['params'], feat_df, self.mode)
            if self.mode == 'train':
                func['params'] = params

        cols = []
        if len(feat_df.shape) == 1:
            cols = [f'{self.index}_0']

        elif len(feat_df.shape) == 2:
            for i in range(feat_df.shape[1]):
                cols.append(f'{self.index}_{i}')

        feat_df.columns = cols
        return feat_df, self.feature_engineer_config

def ordinal(params, col_frame, mode):
    if mode == 'train':
        category_list = col_frame.value_counts().index.tolist()
        params['category_list'] = category_list
    else:
        category_list = params['category_list']
    col_frame[~col_frame.isin(category_list)] = len(category_list)
    for i, cate in enumerate(category_list):
        col_frame[col_frame == cate] = i
    col_frame = col_frame.astype(int)
    return col_frame, params

def one_hot(params, col_frame, mode):
    if mode == 'train':
        category_list = col_frame.value_counts().index.tolist()
        params['category_list'] = category_list
    else:
        category_list = params['category_list']

    col_one_hot = np.zeros((col_frame.shape[0], len(category_list)+1), dtype=np.int32 )

    for i, val in enumerate(col_frame.tolist()):
        if val == val and val in category_list: # not nan
            col_one_hot[i][category_list.index(val)] = 1
        else:
            col_one_hot[i][len(category_list)] = 1

    frame_new = pd.DataFrame(col_one_hot, index=col_frame.index)
    return frame_new, params

def quantile_transform(params, col_frame, mode):
    if mode == 'train':
        bucket_size = params.get('bucket_size', 10)
        boundaries = []
        for pos in range(1, bucket_size):
            boundaries.append(col_frame[~col_frame.isnull()].quantile(pos/bucket_size))
        params['boundaries'] = boundaries
    else:
        boundaries = params['boundaries']

    bins = [float('-inf')]
    bins.extend(boundaries)
    bins.append(float('inf'))

    col_frame[~col_frame.isnull()] = pd.cut(col_frame[~col_frame.isnull()], bins, labels=False, duplicates='drop').astype(int)
    return col_frame, params

def log_transform(params, col_frame, mode):
    assert col_frame[(~col_frame.isnull()) & (col_frame < 0)].empty
    col_frame[~col_frame.isnull()] = np.log10(col_frame[~col_frame.isnull()]+1)
    return col_frame, params

def standard_scale(params, col_frame, mode):
    if mode == 'train':
        mean = col_frame[~col_frame.isnull()].mean()
        std = col_frame[~col_frame.isnull()].std()
        params['mean'] = mean
        params['std'] = std
    else:
        mean = params['mean']
        std = params['std']
    if std == 0:
        col_frame.iloc[:, ] = 1
    else:
        col_frame[~col_frame.isnull()] = (col_frame[~col_frame.isnull()] - mean) / std
    return col_frame, params

def max_abs_scale(params, col_frame, mode):
    if mode == 'train':
        max_abs = col_frame[~col_frame.isnull()].abs().max()
        params['max_abs'] = max_abs
    else:
        max_abs = params['max_abs']

    if max_abs == 0:
        col_frame.iloc[:, ] = 0
    else:
        col_frame[~col_frame.isnull()] = col_frame[~col_frame.isnull()]/max_abs
    return col_frame, params

def min_max_scale(params, col_frame, mode):
    if mode == 'train':
        max = col_frame[~col_frame.isnull()].max()
        min = col_frame[~col_frame.isnull()].min()
        params['max'] = max
        params['min'] = min
    else:
        max = params['max']
        min = params['min']
    if max == min:
        if max == 0:
            col_frame[~col_frame.isnull()].iloc[:, ] = 0
        else:
            col_frame[~col_frame.isnull()].iloc[:, ] = 1
    else:
        col_frame[~col_frame.isnull()] = (col_frame[~col_frame.isnull()] - min)/ (max - min)
    return col_frame, params

def bucket(params, col_frame, mode):
    assert 'boundaries' in params and len(params['boundaries']) > 0
    bins = [float('-inf')]
    bins.extend(params['boundaries'])
    bins.append(float('inf'))
    labels = range(len(bins)-1)
    col_frame[~col_frame.isnull()] = pd.cut(col_frame[~col_frame.isnull()], bins, labels=False, duplicates='drop').astype(int)
    return col_frame, params

def translation(params, col_frame, mode):
    if mode == 'train':
        min = col_frame[~col_frame.isnull()].min()
        params['min'] = min
    else:
        min = params['min']
    if min >= 0:
        return col_frame, params
    col_frame[~col_frame.isnull()] = col_frame[~col_frame.isnull()] + abs(min)
    return col_frame, params

def square(params, col_frame, mode):
    col_frame[~col_frame.isnull()] = np.square(col_frame[~col_frame.isnull()])
    return col_frame, params

def robust_scale(params, col_frame, mode):
    if mode == 'train':
        median = col_frame[~col_frame.isnull()].quantile()
        quant25 = col_frame[~col_frame.isnull()].quantile(0.25)
        quant75 = col_frame[~col_frame.isnull()].quantile(0.75)
        params['median'] = median
        params['quant25'] = quant25
        params['quant75'] = quant75
    else:
        median = params['median']
        quant25 = params['quant25']
        quant75 = params['quant75']
    if quant25 != quant75:
        col_frame[~col_frame.isnull()] = (col_frame[~col_frame.isnull()] - median)/ (quant75 - quant25)
    return col_frame, params

def drop(params, col_frame, mode):
    return pd.DataFrame(), params

def hash_feature(params, col_frame, mode):
    if mode == 'train':
        params['bucket_size'] = params.get('bucket_size', 10)
    hash_bucket_size = params['bucket_size']
    col_frame[~col_frame.isnull()] = col_frame[~col_frame.isnull()].apply(lambda x: hash(x) % hash_bucket_size)
    return col_frame.astype(int), params

def interval_bucket(params, col_frame, mode):
    if mode == 'train':
        bucket_size = params.get('bucket_size', 10)
        boundaries = []
        maxim, minim = col_frame[~col_frame.isnull()].max(), col_frame[~col_frame.isnull()].min()
        for pos in range(1, bucket_size):
            boundaries.append((maxim - minim)*pos/bucket_size + minim)
        params['boundaries'] = boundaries
    else:
        boundaries = params['boundaries']

    bins = [float('-inf')]
    bins.extend(boundaries)
    bins.append(float('inf'))

    col_frame[~col_frame.isnull()] = pd.cut(col_frame[~col_frame.isnull()], bins, labels=False, duplicates='drop').astype(int)
    return col_frame, params

def kmeans_bucket(params, col_frame, mode):
    data = col_frame[~col_frame.isnull()].to_numpy().reshape(-1, 1)
    if mode == 'train':
        n_clusters = params.get('bucket_size', 10)
        kmeans = KMeans(n_clusters=n_clusters).fit(data)
        centers = kmeans.cluster_centers_
        params['cluster_centers'] = centers
    else:
        centers = params['cluster_centers']

    dist = []
    for c in centers:
        dist.append(abs(data - c).reshape(-1))
    label = np.array(dist).argmin(axis=0)
    col_frame[~col_frame.isnull()] = label
    return col_frame, params