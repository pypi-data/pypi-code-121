#!/usr/bin/env python
# coding: utf-8
import argparse
import os
from re import L

import yaml
from intelliw.config.cfg_parser import load_config
from intelliw.utils.util import to_type

pre_predict = "pre-predict"
post_predict = "post-predict"
packages_path = "/root/packages"
infer_path = "/root/intelliw/infer"
lib_dict = "lib"
conf_dict = "conf"
plain_http_name = "plainhttp.so"
plain_infer_name = "plaininfer.so"
sys_log_name = "syslog.xml"
infer_config_name = "infer_model.yaml"
model_yaml = "model.yaml"
endpoint = "/predict"
queue_length = 100
cpu_count = os.cpu_count()
# funcs_mapping = {
#     'sys.general.getvalue': "general_filter.GetValue",
#     'sys.image.decode': "gocv_filter.ImDecode",
#     'sys.image.resize': "gocv_filter.ImResize",
#     'sys.image.transpose': "gocv_filter.ImTranspose",
#     'sys.matrix.normalize': "matrix_filter.Normalize",
#     'sys.matrix.reshape': "matrix_filter.Reshape",
#     'sys.matrix.transpose': "matrix_filter.Transpose",
#     'sys.post.argmax': "postprocess_filter.Argmax",
#     'sys.post.process': "postprocess_filter.PostProcess"}

funcs_mapping = {
    'sys.general.getvalue': "general_filter.GetValue",
    'sys.general.base64decode': "general_filter.Base64Decode",
    'sys.gocv.bytes2mat': "gocv_filter.Bytes2Mat",
    'sys.gocv.astype': "gocv_filter.Astype",
    'sys.gongshang.normalize': "gongshang_filter.Normalize",

    'sys.tensor.array2tensor': "tensor_filter.Array2Tensor",
    'sys.tensor.transpose': "tensor_filter.Transpose",
    'sys.tensor.reshape': "tensor_filter.Reshape",
    'sys.tensor.tensor2array': "tensor_filter.Tensor2Array",
    'sys.general.genmapinput': "general_filter.GenMapInput",

    'sys.general.index': "general_filter.Index",
    'sys.gongshang.postprocess': "gongshang_filter.PostProcess",
    'sys.general.print': "general_filter.Print",
    }



def convert_model_config(path):
    cfg = load_config(os.path.join(path, model_yaml))
    model = cfg['Model']
    if "processor" not in model:
        raise KeyError("processor not in model.yaml")

    infer_cfg = dict()
    infer_cfg["Model"] = cfg['Model']
    infer_cfg = gen_default_cfg(infer_cfg)
    

    engine_name, engine_plugin = convert_engine(path, model)
    infer_cfg["Infer"]["modules"].append(engine_plugin)
    infer_cfg["Infer"]["queueLength"] = cpu_count * queue_length

    modules = set("")
    plugin_infer = gen_infer_plugin(model["transforms"], engine_name, modules)

    file_list = file_name(os.path.join(path, lib_dict))
    for name in modules:
        plugin = dict()
        plugin["name"] = name
        if name in file_list:
            plugin["location"] = os.path.join(path, lib_dict, name + ".so")
            plugin["type"] = "pfilter"
        else:
            plugin["location"] = os.path.join(infer_path, lib_dict, name + ".so")
            plugin["type"] = "filter"
        infer_cfg["Infer"]["modules"].append(plugin)

    http_plugin = gen_http_plugin(None, plugin_infer)
    infer_cfg["Infer"]["modules"].append(http_plugin)
    
    save_config(os.path.join(path, model_yaml), infer_cfg)


# 生成http插件配置
def gen_http_plugin(http_module, plugin_infer):
    if http_module is not None:
        plugin_http = http_module
        params = convert_params(http_module["parameters"])
        plugin_http["parameters"] = params
    else:
        plugin_http = dict()
        plugin_http["name"] = "plainhttp"
        plugin_http["type"] = "http"
        plugin_http["location"] = os.path.join(infer_path, lib_dict, plain_http_name)
        plugin_http["parameters"] = list()
        plugin_http["parameters"].append({"location": endpoint})

    plugin_http["modules"] = list()
    plugin_http["modules"].append(plugin_infer)

    return plugin_http


# 生成infer推理插件配置
def gen_infer_plugin(transforms, engine_name, modules):
    plugin_infer = dict()
    plugin_infer["name"] = "plaininfer"
    plugin_infer["type"] = "infer"
    plugin_infer["ref"] = engine_name
    plugin_infer["location"] = os.path.join(infer_path, lib_dict, plain_infer_name)
    plugin_infer["parameters"] = list()
    plugin_infer["parameters"].append({"workerCount": cpu_count})

    if transforms is None:
        return plugin_infer
    trans = list()
    for transform in transforms:
        if transform["type"] != pre_predict and transform["type"] != post_predict:
            raise KeyError("transform type {} is not supported".format(transform["type"]))
        infer_transform = dict()
        infer_transform["type"] = transform["type"]
        infer_transform["functions"] = list()
        for func in transform["functions"]:
            infer_func = dict()
            if func["key"] in funcs_mapping:
                func_name = funcs_mapping[func["key"]]
                infer_func["function"] = func_name
                modules.add(func_name.split(".")[0])
            else:
                raise KeyError("function {} unsupported".format(func["key"]))
            if "parameters" in func:
                params = convert_params(func["parameters"])
                #过滤 - function: general_filter.Print 
                #       parameters:
                #       - {}
                if len(params)==1 and len(params[0])!=0:
                  infer_func["parameters"] = params
            infer_transform["functions"].append(infer_func)
        # if transform["type"] == pre_predict:
        #     # 生成golang框架最后一个隐含的function
        #     genInputFunc = dict()
        #     genInputFunc["function"] = "general_filter.GenTensorflowInput"
        #     genInputFunc["parameters"] = [{"names": ["input_1"]}]
        #     infer_transform["functions"].append(genInputFunc)
        trans.append(infer_transform)
    plugin_infer["transforms"] = trans
    return plugin_infer


# 生成engine适配器插件配置
def convert_engine(path, model):
    algorithm = model["algorithm"]
    plugin_engine = dict()
    if "type" not in model["processor"]:
        raise KeyError("must input processor type field")
    processor_type = model["processor"]["type"]
    plugin_engine["name"] = processor_type
    plugin_engine["type"] = "engine"
    # engine_name = algorithm["processor"] + "Engine" + str(algorithm["version"]).capitalize() + ".so"
    engine_name = processor_type + "Engine" + ".so"
    plugin_engine["location"] = os.path.join(infer_path, lib_dict, engine_name)
    if "parameters" in algorithm:
        params = convert_params(algorithm["parameters"])
        plugin_engine["parameters"] = params
    else:
        plugin_engine["parameters"] = list()

    if len(plugin_engine["parameters"]) == 0:
        params = dict()
        params["tags"] = ["serve"]
        params["targets"] = ["dense_2/Sigmoid"]
        params["inputs"] = ["input_1"]
        plugin_engine["parameters"].append(params)

    model_path = str(model["location"])
    if model_path.startswith("./"):
        model_path = model_path.replace("./", "")

    #plugin_engine["parameters"][0]["modelPath"] = os.path.join(path, model_path, "hp")
    plugin_engine["parameters"][0]["modelPath"] = os.path.join(path, model_path)

    return plugin_engine["name"], plugin_engine


def convert_params(params):
    if params is None:
        return None
    li = list()
    p = dict()
    li.append(p)
    for param in params:
        option = param['option'] if 'option' in param else None
        if option is not None and 'type' in option:
            p[param["key"]] = to_type(param["val"], option['type'])
        else:
            p[param["key"]] = param["val"]
    return li


def gen_default_cfg(default):
    default["Infer"]=dict()
    default["Infer"]["server"] = dict()
    default["Infer"]["server"]["host"] = ":8888"
    default["Infer"]["server"]["log"] = os.path.join(infer_path, conf_dict, sys_log_name)
    default["Infer"]["server"]["readtimeout"] = 3000
    default["Infer"]["server"]["writetimeout"] = 3000
    default["Infer"]["modules"] = list()
    
    return default


def save_config(path, cfg):
    with open(path, 'w',encoding='utf-8') as file:
        documents = yaml.dump(cfg, file, default_flow_style=False,allow_unicode=True,sort_keys=False)


def file_name(file_dir):   
         file_list=[]   
         for root, dirs, files in os.walk(file_dir):  
             for file in files:  
                 if os.path.splitext(file)[1].lower() == '.so':  
                     file_list.append(os.path.splitext(file)[0])  
         return file_list

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("-p", "--path", type=str, help="iwm path")
    args = parser.parse_args()
    print("path is {}".format(args.path))
    convert_model_config(args.path)
    # L=file_name("./lib")
    # print(L)

