import uuid
import os
import socket
from datetime import datetime
import yaml
from miacag.preprocessing.split_train_val import splitter
from miacag.utils.sql_utils import copy_table, add_columns
import pandas as pd
from miacag.postprocessing.append_results import appendDataFrame
import torch
from miacag.trainer import train
from miacag.tester import test
from miacag.configs.config import load_config, maybe_create_tensorboard_logdir
from miacag.configs.options import TrainOptions
import argparse
from miacag.preprocessing.labels_map import labelsMap
from miacag.preprocessing.utils.check_experiments import checkExpExists, \
    checkCsvExists
from miacag.plots.plotter import plot_results
import pandas as pd
from miacag.utils.script_utils import create_empty_csv, mkFolder


parser = argparse.ArgumentParser(
            formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument(
    '--cpu', type=str,
    help="if cpu 'True' else 'False'")
parser.add_argument(
            "--local_rank", type=int,
            help="Local rank: torch.distributed.launch.")    
parser.add_argument(
            "--num_workers", type=int,
            help="Number of cpu workers for training")
parser.add_argument(
    '--config_path', type=str,
    help="path to folder with config files")


def angio_classifier(cpu, num_workers, config_path):
    torch.distributed.init_process_group(
            backend="nccl" if cpu == "False" else "Gloo",
            init_method="env://"
            )
    config_path = [
        os.path.join(config_path, i) for i in os.listdir(config_path)]

    for i in range(0, len(config_path)):
        print('loading config:', config_path[i])
        with open(config_path[i]) as file:
            config = yaml.load(file, Loader=yaml.FullLoader)
        mkFolder(config['output'])
        csv_exists, output_csv_test = checkCsvExists(config['output'])
        if csv_exists is False:
            trans_label = \
                [i + '_transformed' for i in config['labels_names']]
            df_results = create_empty_csv(output_csv_test, trans_label)
        else:
            df_results = pd.read_csv(output_csv_test)

        exp_exists = checkExpExists(config_path[i], config['output'])
        if exp_exists is False:

            config['master_port'] = os.environ['MASTER_PORT']
            config['num_workers'] = num_workers
            config['cpu'] = cpu
            tensorboard_comment = os.path.basename(config_path[i])[:-5]
            torch.distributed.barrier()
            experiment_name = tensorboard_comment + '_' + \
                "SEP_" + \
                datetime.now().strftime('%b%d_%H-%M-%S') \
                + '_' + socket.gethostname()
            torch.distributed.barrier()
            output_directory = os.path.join(
                        config['output'],
                        experiment_name)
            mkFolder(output_directory)
            output_config = os.path.join(output_directory,
                                         os.path.basename(config_path[i]))

            output_table_name = experiment_name + "_" + config['table_name']

            output_plots = os.path.join(output_directory, 'plots')
            mkFolder(output_plots)

            output_plots_train = os.path.join(output_plots, 'train')
            output_plots_val = os.path.join(output_plots, 'val')
            output_plots_test = os.path.join(output_plots, 'test')

            mkFolder(output_plots_train)
            mkFolder(output_plots_test)
            mkFolder(output_plots_val)

            # begin pipeline
            # 1. copy table
            os.system("mkdir -p {output_dir}".format(
                output_dir=output_directory))
            torch.distributed.barrier()
            if torch.distributed.get_rank() == 0:

                copy_table(sql_config={
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'table_name_input': config['table_name'],
                    'table_name_output': output_table_name})

                # # 2. copy config
                os.system(
                    "cp {config_path} {config_file_temp}".format(
                        config_path=config_path[i],
                        config_file_temp=output_config))
                # map labels
                mapper_obj = labelsMap(
                    {
                        'labels_names': config['labels_names'],
                        'database': config['database'],
                        'username': config['username'],
                        'password': config['password'],
                        'host': config['host'],
                        'table_name': output_table_name,
                        'query': config['query_test'],
                        'TestSize': 1},
                    config['labels_dict'])
                mapper_obj()
            trans_labels = [i + '_transformed' for i in config['labels_names']]
            config['labels_names'] = trans_labels

            # add placeholder for confidences
            conf = [i + '_confidences' for i in config['labels_names']]

            # add placeholder for predictions
            pred = [i + '_predictions' for i in config['labels_names']]
            torch.distributed.barrier()
            if torch.distributed.get_rank() == 0:
                add_columns({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'table_name': output_table_name,
                    'table_name_output': output_table_name},
                            conf,
                            ["VARCHAR"] * len(conf))

                add_columns({
                    'database': config['database'],
                    'username': config['username'],
                    'password': config['password'],
                    'host': config['host'],
                    'table_name': output_table_name,
                    'table_name_output': output_table_name},
                            pred,
                            ["float8"] * len(pred)
                            )
                # 3. split train and validation , and map labels
                splitter_obj = splitter(
                    {
                     'labels_names': config['labels_names'],
                     'database': config['database'],
                     'username': config['username'],
                     'password': config['password'],
                     'host': config['host'],
                     'table_name': output_table_name,
                     'query': config['query'],
                     'TestSize': config['TestSize']},
                    config['labels_dict'])
                splitter_obj()
                # ...and map data['labels'] test
            torch.distributed.barrier()
            # 4. Train model
            config['output'] = output_directory
            config['output_directory'] = output_directory
            config['table_name'] = output_table_name
            config['use_DDP'] = 'True'
            config['datasetFingerprintFile'] = None
            train(config)

            # 5 eval model

            config['model']['pretrain_model'] = output_directory
            test({**config, 'query': config["query_test"], 'TestSize': 1})

            # plotting results
            torch.distributed.barrier()
            if torch.distributed.get_rank() == 0:
                # 6 plot results:
                # train
                plot_results({
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'labels_names': config['labels_names'],
                            'table_name': output_table_name,
                            'query': config['query_train_plot']},
                            output_plots_train,
                            config['model']['num_classes']
                            )
                # val
                plot_results({
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'labels_names': config['labels_names'],
                            'table_name': output_table_name,
                            'query': config['query_val_plot']},
                            output_plots_val,
                            config['model']['num_classes']
                            )
                # test
                plot_results({
                            'database': config['database'],
                            'username': config['username'],
                            'password': config['password'],
                            'host': config['host'],
                            'labels_names': config['labels_names'],
                            'table_name': output_table_name,
                            'query': config['query_test_plot']},
                            output_plots_test,
                            config['model']['num_classes']
                            )

                csv_results = appendDataFrame(sql_config={
                                    'labels_names': config['labels_names'],
                                    'database': config['database'],
                                    'username': config['username'],
                                    'password': config['password'],
                                    'host': config['host'],
                                    'table_name': output_table_name,
                                    'query': config['query_test_plot']},
                                df_results=df_results,
                                experiment_name=experiment_name)
                print('config files processed', str(i+1))
                print('config files to process in toal:', len(config_path))
                csv_results = pd.DataFrame(csv_results)
                csv_results.to_csv(output_csv_test, index=False, header=True)
        if csv_exists:
            return None
        else:
            return output_table_name


if __name__ == '__main__':
    args = parser.parse_args()

    angio_classifier(args.cpu, args.num_workers, args.config_path)
