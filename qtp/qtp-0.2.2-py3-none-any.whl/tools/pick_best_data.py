import pandas as pd
from qtp.tools.hun_dropbox import HunDropbox

class PickBestData:
    def __init__(self, args):
        self.box      = HunDropbox(args['dropbox_token'])
        self.path     = args['path']
        self.exchange = args['exchange']
        self.strategy = args['strategy']
        self.backtest = args['backtest']

        self.hpr                 = args['hpr']
        self.tradings_days_ratio = args['tradings_days_ratio']
        self.taking_days_max     = args['taking_days_max']
        self.save_path           = args['save_path']

    def save_json(self):
        try:
            name = self.__file_name() + '.json'
            self.box.save_json(self.save_path, name, self.__best_param())
        except IndexError:
            print('IndexError: 조건에 해당 되는 파일이 없는것으로 추측 되네요')

    def read_json(self):
        name = self.__file_name() + '.json'
        data = self.box.read_json(self.save_path, name,)
        return data

    def strategy_file(self):
        list = self.__file_list()
        name = self.__file_name()
        csv = [csv for csv in list if csv.startswith(name)]
        csv.sort()
        return csv[-1]

    def __best_param(self):
        strategy_file_name = self.strategy_file()
        strategy_df = self.__read_csv(strategy_file_name)
        best_param = self.__get_best_data(strategy_df)
        return best_param

    def __get_best_data(self, strategy_df):
        df = strategy_df
        best_datas = []
        for market in df['market'].drop_duplicates().values:
            con0 = (df['market'] == market)
            con1 = (df['hpr'] > self.hpr)
            con2 = (df['tradings_days_ratio']) > self.tradings_days_ratio
            con3 = (df['taking_days_max']) < self.taking_days_max
            marekt_df = df[con0 & con1 & con2 & con3]
            marekt_df = marekt_df.sort_values(by=['hpr', 'tradings_days_ratio'])

            if marekt_df.empty:
                raise Exception(f"{market}는 존재하지만 조건에 맞는 데이터 없음")
            else:
                _ = marekt_df.iloc[-1].to_dict()
                best_datas.append(_)

        return best_datas

    def __read_csv(self, strategy_file_name):
        df = self.box.read_csv_without_index(self.path, strategy_file_name)
        return df

    def __file_name(self):
        name = f'{self.exchange}-{self.strategy}-{self.backtest}'
        return name

    def __file_list(self):
        file_list = self.box.get_file_list(self.path)
        return file_list
