import datetime
import re
from os import mkdir, makedirs
from os.path import exists, join

import gdown
import pandas as pd

from log_datasets.dataset import Dataset
from utils.Drain import LogParser


class HDFSDataset(Dataset):
    def __init__(self, data_folder_path="../data"):
        Dataset.__init__(self, data_folder_path)

    @staticmethod
    def __find(params):
        for x in eval(params):
            if "blk" in x:
                match = re.search('(.*)(blk_(-*\d*))(.*)', x)
                return match.group(2)
        return None

    def load_logs(self):

        # download raw logs
        output_path = f"{self.data_folder_path}/hdfs/HDFS.log"
        # 189R1qzhTMLQYo2llwse5F-InsFxBbxr-
        url = 'https://drive.google.com/uc?id=189R1qzhTMLQYo2llwse5F-InsFxBbxr-'
        if not exists(output_path):
            mkdir(join(f"{self.data_folder_path}/hdfs"))
            gdown.download(url, output_path, quiet=False)

        if not exists(f"{self.data_folder_path}/hdfs/HDFS.log_structured.csv"):
            input_dir = f"{self.data_folder_path}/hdfs/"
            output_dir = f"{self.data_folder_path}/hdfs/"
            log_file = 'HDFS.log'
            log_format = "<Date> <Time> <Pid> <Level> <Component>: <Content>"

            # Regular expression list for optional preprocessing (default: [])
            regex = [
                r'blk_(|-)[0-9]+',  # block id
                r'(/|)([0-9]+\.){3}[0-9]+(:[0-9]+|)(:|)',  # IP
                r'(?<=[^A-Za-z0-9])(\-?\+?\d+)(?=[^A-Za-z0-9])|[0-9]+$',  # Numbers
            ]
            st = 0.5  # Similarity threshold
            depth = 2  # Depth of all leaf nodes

            parser = LogParser(log_format, indir=input_dir, outdir=output_dir, depth=depth, st=st, rex=regex)
            parser.parse(log_file)

        self.logs = pd.read_csv(f"{self.data_folder_path}/hdfs/HDFS.log_structured.csv")
        self.logs = self.logs.iloc[1:, :]
        dates = {81109: "2008-11-9", 81110: "2008-11-10", 81111: "2008-11-11"}
        self.logs['Date'] = self.logs['Date'].apply(lambda x: dates[x])
        self.logs['Time'] = self.logs['Time'].apply(
            lambda x: datetime.datetime.strptime(str(x).zfill(6), "%H%M%S").strftime("%H:%M:%S"))
        self.logs['timestamp'] = pd.to_datetime(self.logs['Date'] + " " + self.logs['Time'])
        self.logs['EventId'] = self.logs['EventId'].astype('str')
        self.logs['block_id'] = self.logs['ParameterList'].apply(lambda x: self.__find(x))
        self.logs['block_id'] = self.logs['block_id'].astype('str')
        self.logs.sort_values(['timestamp'], inplace=True)

        self.logs = self.logs[['timestamp', 'EventId', 'block_id']]
        self.logs.rename(columns={'timestamp': 'timestamp', 'EventId': 'event_id', 'block_id': 'session_id'},
                         inplace=True)

    def load_event_templates(self):
        output_path = f'{self.data_folder_path}/hdfs/HDFS.log_templates.csv'
        self.templates = pd.read_csv(output_path)

    def assign_event_id_to_logs(self):
        """
        This dataset already has event IDs attached to the logs
        :return:
        """
        pass

    def print_sample(self):
        print(self.logs.head(20))


class BGLDataset(Dataset):
    def __init__(self, data_folder_path="../data"):
        Dataset.__init__(self, data_folder_path)

    def load_logs(self):
        output_file = f'{self.data_folder_path}/bgl/unparsed/logs.log'
        url = 'https://drive.google.com/uc?id=1qlYZB26biKt7jlxL8YmIXHlqqeMDv-iX'

        if not exists(f'{self.data_folder_path}/bgl/'):
            makedirs(f'{self.data_folder_path}/bgl/')

        if not exists(f'{self.data_folder_path}/bgl/unparsed'):
            makedirs(f'{self.data_folder_path}/bgl/unparsed')
            gdown.download(url, output_file, quiet=False)

        # Replace the commas with semicolons
        # commas cause problems with DRAIN and writing to csv
        log_file = f'{self.data_folder_path}/bgl/unparsed/processed_logs.log'

        lf = open(log_file, 'a')

        with open(output_file) as of:
            for line in of:
                lf.write(line.replace(',', ';'))

        lf.close()

        # Parse the logs with DRAIN
        log_file = 'processed_logs.log'
        input_dir = f'{self.data_folder_path}/bgl/unparsed/'
        output_dir = f'{self.data_folder_path}/bgl/'
        log_format = "<Label> <Timestamp> <Date> <Node> <Time> <NodeRepeat> <Type> <Component> <Level> <Content>"

        parser = LogParser(log_format, indir=input_dir, outdir=output_dir)
        parser.parse(log_file)

        self.logs = pd.read_csv(output_dir + 'processed_logs.log_structured.csv')
        self.templates=pd.read_csv(output_dir + 'processed_logs.log_templates.csv')
        self.logs['Time'] = pd.to_datetime(self.logs['Time'], format='%Y-%m-%d-%H.%M.%S.%f')
        self.logs.sort_values(['Time'])

        self.logs = self.logs[['Time', 'EventId']]
        self.logs.rename(columns={'Time': 'timestamp', 'EventId': 'event_id'}, inplace=True)
        print(self.logs.head())
        print(len(self.logs))

    def load_event_templates(self):
        """
        Drain has already extracted the event templates, do nothing.
        """
        pass

    def assign_event_id_to_logs(self):
        """
        BGL already has event ids, do nothing.
        """
        pass


class NovaDataset(Dataset):
    def __init__(self, data_folder_path="../data"):
        Dataset.__init__(self, data_folder_path)
        self.anomalous_logs = ['f680c053', '40206f48', 'c9043c44', 'c03dad2d', 'ef6e7b9e', 'e666ec6f', '6d765f31', '879ea5bb', 'c9c98d3b', '895eb283', 'ec253f87', 'a72188c8', 'a987a892', 'e0d2142b', '0f2ef0f1', 'e58cad65', 'b5d66d95', 'af901f3b', '7a899844', '54eb1be1', '1d12462b', 'b8e9463c', '095edf34', 'ec7fa6ce', 'daff47bf', '59e838c8', '53a5a044', '9a2c8541', 'd12829f8', '0ab3cef6', '041f292c', 'd6d9af41', 'ba88c7d8', '8df33b2f', '1544fa1c', '6065c610', '485a2872', 'a0c9927d', '8c9b4bef', 'e54a6a63', '1123e884', 'e599e359', '4d89da7e', '808039a9', 'eb99df1b', '8fe5e47c', '9a35f684', '7fd638a9', 'bd1518d3', '85222adb', '875b7935', '29edf214', 'c7af4a07', 'cdc8c0bb', '1289b10d', '525d19dd', '7981fd0c', '7366954a', '252847ed', '6aab68e3', '7d5b1608', '44aebf8e', '9483c621', 'e00d67e7', '5b547994', 'b8052b25', '58995305', 'de919eb5', 'b71472cf', '6ec5a18d', 'b2ffd2be', 'a0d89467', '73ee123d', '32d1c10f', '54a4f708', '7a1b07cd', '260be159', '9064dde6', 'b216dde5', '072292e8', '090149fe', '2bb55381', '1553c20a', 'a47b8c12', 'f9547a6c', 'aa4549b8', '00222bb8', 'd82cb15d', '0a102ea5', '50fcf2f8', '91f835b0', 'd95e1207', '0f7a78c1', 'acd26318', '4355a1db', '2e1a0cd9', '57fe8e47', '7b3e2eac', '622b6a3f', '675f1d72', '6d53c0af', 'd793c869', '94f0ba06', 'a2926c3f', '0fd492f7', '0e080610', 'd530dea3', 'a5e60942', '06f86f88', '5d64a93f', '4116c241', '577304d2', '5e2ba79a', 'aa213323', '64637844', 'bac0f26e', 'd1fcc31d', '6899ef8a', 'e0099b85', 'bd6f6bbc', 'aadd25f4', 'b8f641dc', '12e244f2', '756f5c03', '05401b4f', 'fd8f1a5e', '02525647', '319130ea', '58591b5c', '02e5bdf8', 'fa83b19b', '8861c737', '3fb2a127', '1adb2a42', '2400b11f', '8ce81960', 'e4060487', '2b548192', '699ceb91', 'f7b46d4a', '7c3e51b9', '3327ffcf', 'b586d301', 'f74207da', '8b699885', '3d635119', 'c8b73b91', '8ecc3813', '5a36a457', 'b5794355', '66cf9d79', '4d3bf8f6', 'ea3a8254', '92dbdc40', '2b3681ad', 'a58526ac', '4cace397', '9193527c', 'd70b9e96', '95e880a1', 'bea1ad5c', '42c593ba', 'ee7f1b31', 'f28720ba', 'b76bada8', '4942406d', '3cb0ad99']


    def load_logs(self):
        output_path = f'{self.data_folder_path}/nova/logs.csv'
        url = 'https://drive.google.com/uc?id=1Lf-kmpf6OP1WpKT_KkZeUT745CV168gb'
        if not exists(output_path):
            mkdir(f"{self.data_folder_path}/nova")
            gdown.download(url, output_path, quiet=False)

        self.logs = pd.read_csv(output_path)
        self.logs = self.logs.iloc[1:, :]
        self.logs['test_id'] = self.logs['test_id'].astype('int')
        self.logs['time_hour'] = pd.to_datetime(self.logs['time_hour'])
        self.logs.sort_values(['time_hour'])

        self.logs = self.logs[['test_id', 'time_hour', 'EventId']]
        self.logs.rename(columns={'time_hour': 'timestamp', 'EventId': 'event_id'}, inplace=True)
        print(self.logs.head())
        print(len(self.logs))

    def load_event_templates(self):
        output_path = f'{self.data_folder_path}/nova/event_templates.csv'
        url = 'https://drive.google.com/uc?id=1SZqgSvUhvwZTofKslo21U3z2VEBbU17w'
        if not exists(output_path):
            gdown.download(url, output_path, quiet=False)
        self.templates = pd.read_csv(f'{self.data_folder_path}/nova/event_templates.csv')

    def assign_event_id_to_logs(self):
        """
        This dataset already has event IDs attached to the logs
        :return:
        """
        pass


if __name__ == '__main__':
    dataset = BGLDataset("../../data")
    dataset.initialize_dataset()
    graphs = dataset.create_graphs(window_type='sliding', window_size=60000, window_slide=30000, test_id=1,
                                   include_last=False)
    for graph in graphs:
        print (graph)
