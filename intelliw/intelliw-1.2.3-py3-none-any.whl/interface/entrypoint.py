'''
Author: hexu
Date: 2021-10-25 15:20:34
LastEditTime: 2022-05-17 18:12:41
LastEditors: Hexu
Description: 本地使用和安装包的入口文件
FilePath: /iw-algo-fx/intelliw/interface/entrypoint.py
'''

import argparse
import os
import zipfile
import shutil
import intelliw
import intelliw.interface.controller as controller
from intelliw.utils.gen_model_cfg import generate_model_config_from_algorithm_config as __generate
from intelliw.config import config


def __parse_args():
    parser = argparse.ArgumentParser(description="Entry files for local debug and pypi packages")

    parser.add_argument("-p", "--path", default=os.getcwd(),type=str, help="project's path, default is 'os.getcwd()'")
    parser.add_argument("-o", "--output_path", default="target",type=str, help="package file output path")
    parser.add_argument("task", nargs="?", default="version", type=str,
                        help="version: intelliw version | init: initialize the product | init_docs: initialize the document | init_debug: initialize the debug file | import_alg | import_model | train | infer | dataset |  package_iwa | package_iwm | package_iwp | default is 'import_alg'")

    init = parser.add_argument_group('[init/init_docs/init_debug]', description='intelliw init -o output_path -n mydemo')
    init.add_argument("-n", "--name", default="example",type=str, help="algorithms name")

    train = parser.add_argument_group('[train]', description='intelliw train -p project_path -r train_set_ratio')
    train.add_argument("-c", "--csv", default="data.csv",type=str, help="path of csv files as training data")
    train.add_argument('-r', "--train_ratio", default=0.7, type=float, help="train ratio, between 0.0 and 1.0, default is 0.7")
    train.add_argument("-d", "--dataset", default="", type=str, help="dataset id by aiworker")

    infer = parser.add_argument_group('[infer]', description='intelliw infer -p project_path -P 8080')
    infer.add_argument("-P", "--port", default=8888,type=int, help="port to listen, default: 8888")

    parser.add_argument_group('[package_iwa/package_iwm]', description='intelliw package_iwa -p project_path -o output_path; package help: zip algorithms to iwa/iwm')
    parser.add_argument_group('[import_alg/import_model]', description='intelliw import_alg -p project_path; import help: test algorithm import')

    return parser.parse_args()


def __rowAddress():
    addr = config.INPUT_GETROW_ADDR
    if config.SOURCE_TYPE in (4,5):
        return addr
    else:
        mid = config.INPUT_MODEL_ID
        return f"{addr}/{mid}/null"


def __args_to_framework_arg(args, path):
    framework_args = controller.FrameworkArgs()
    framework_args.path = path
    
    if args.task == 'train':
        framework_args.task = 'train'
        framework_args.input = config.INPUT_ADDR
        framework_args.rownumaddr = __rowAddress()
    elif args.task == 'infer':
        framework_args.port = args.port
    
    task_map = {'import_alg': 'importalg', 'import_model': 'importmodel',
                'train': 'batchservice', 'infer': 'apiservice'}
    framework_args.method = task_map.get(args.task)
    assert framework_args.method is not None,'failed to execute, unknown task: {}'.format(args.task)
    return framework_args



def __package(task: str, alg_path: str, output_path: str):
    alg_path = os.path.abspath(alg_path)
    dir_name = os.path.basename(alg_path)
    if task == 'package' or task == 'package_iwa':
        file_name = dir_name + '.iwa'
    elif task == 'package_iwm':
        file_name = dir_name + '.iwm'
    elif task == 'package_iwp':
        file_name = dir_name + '.iwp'
    else:
        raise ValueError('Unknown package task: {}, supported task are package, package_iwa and package_iwm'
                         .format(task))

    output_path = os.path.abspath(output_path)
    output = os.path.join(output_path, file_name)
    # 创建保存的文件夹
    if not os.path.exists(output_path):
        os.makedirs(output_path)
    # 删除存在的文件
    if os.path.exists(output):
        os.remove(output)

    with zipfile.ZipFile(output, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, _, files in os.walk(alg_path):
            if root.endswith('__pycache__') or root.endswith('.git') or root.endswith('.idea'):
                continue

            relative_path = root.replace(alg_path, "")
            if relative_path.startswith(os.sep):
                relative_path = relative_path[len(os.sep):]
            output_relative_path = os.path.join(dir_name, relative_path)
            for file in files:
                if file.startswith('.DS_Store'):
                    continue
                print(os.path.join(root, file), " to zip file:",
                      os.path.join(output_relative_path, file))
                zipf.write(os.path.join(root, file),
                           os.path.join(output_relative_path, file))


def __init_algorithms(name: str, output_path: str, task: str):
    package_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    def alter(file, old_str, new_str):
        file_data = ""
        with open(file, "r", encoding="utf-8") as f:
            for line in f:
                if old_str in line:
                    line = line.replace(old_str, new_str)
                file_data += line
        with open(file, "w", encoding="utf-8") as f:
            f.write(file_data)

    if output_path == "target":
        output_path = os.getcwd()

    if not os.path.exists(output_path):
        raise FileNotFoundError(f"No such file or directory: '{output_path}'")

    if task == "init_docs":
        docs_dir = os.path.join(package_path, "docs")
        shutil.copytree(docs_dir, os.path.join(output_path, "docs"))
    if task == "init_debug":
        debug_file = os.path.join(package_path, "utils", "debug_contorler.py")
        shutil.copyfile(debug_file, os.path.join(
            output_path, "debug_contorler.py"))
    else:
        output_path = os.path.join(output_path, name)
        algorithms_dir = os.path.join(package_path, "algorithms_demo")
        algorithm_yaml = os.path.join(output_path, "algorithm.yaml")
        shutil.copytree(algorithms_dir, output_path)

        docs_dir = os.path.join(package_path, "docs")
        output_docs_dir = os.path.join(output_path, "docs")
        shutil.copytree(docs_dir, output_docs_dir)

        debug_file = os.path.join(package_path, "utils", "debug_contorler.py")
        output_debug_file = os.path.join(output_path, "debug_contorler.py")
        shutil.copyfile(debug_file, output_debug_file)

        alter(algorithm_yaml, "AlgorithmName", name)

        pycache = os.path.join(name, "__pycache__")
        if os.path.exists(pycache):
            shutil.rmtree(pycache)

def __dataset(dataset_id=None, train_ratio=None, loacl_csv=None):
    config.set_dataset_config(dataset_id, train_ratio, loacl_csv)

def run():
    args = __parse_args()
    config.update_by_env()

    # version
    if args.task.startswith("version"):
        print(f"intelliw version: {intelliw.__version__}")
        return

    # init
    if args.task.startswith("init"):
        __init_algorithms(args.name, args.output_path, args.task)
        return

    # package
    if args.task.startswith("package"):
        __package(args.task, args.path, args.output_path)
        return

    # set dataset
    if args.task.startswith("dataset"):
        __dataset(args.dataset)

    # set task
    if args.task == 'train':
        model_yaml_path, algo_yaml_path = os.path.join(
            args.path, 'model.yaml'), os.path.join(args.path, 'algorithm.yaml')
        __generate(algo_yaml_path, model_yaml_path)
        __dataset(args.dataset, args.train_ratio, args.csv)

    framework_args = __args_to_framework_arg(args, args.path)
    config.RUNNING_MODE = 'SCAFFOLDING'
    controller.main(framework_args)


if __name__ == '__main__':
    run()
    # __init_algorithms()
