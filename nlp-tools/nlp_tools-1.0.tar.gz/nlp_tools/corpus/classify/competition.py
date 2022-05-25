import pandas as pd
from nlp_tools import utils

class DataFoundClassify():
    '''
    第五届“达观杯” 基于大规模预训练模型的风险事件标签识别
    https://www.datafountain.cn/competitions/512
    '''

    @classmethod
    def load_data(cls,
                  file_name: str ,
                  shuffle: bool = True):
        data_df = pd.read_csv(file_name)
        x_data = data_df['text'].tolist()
        y_data = data_df['label'].tolist()

        
        if shuffle:
            x_data, y_data = utils.unison_shuffled_copies(x_data, y_data)

        data_union = [(x, y) for x, y in zip(x_data, y_data)]
        return data_union


if __name__ == '__main__':
    data_path = r'/home/qiufengfeng/nlp/competition/datagrand/基于大规模预训练模型的风险事件标签识别/processed/train.csv'

    DataFoundClassify().load_data(file_name=data_path)