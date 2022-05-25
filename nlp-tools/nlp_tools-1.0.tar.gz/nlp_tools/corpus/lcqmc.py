from typing import Tuple, List
import random



class LCQMC(object):
    __corpus_name__ = 'lcqmc'

    @classmethod
    def load_data(cls,
                  file_path: str ,
                  shuffle: bool = True):
        """
                Args:
                    file_path: file ablsute path
                    shuffle: should shuffle or not, default True.

                Returns:
                    dataset_features and dataset labels
                """
        data = []
        with open(file_path,'r',encoding='utf-8') as fread:
            for index, line in enumerate(fread):
                x1,x2,label = line.strip().split("\t")
                data.append(([x1,x2],str(label)))

        if shuffle:
            random.shuffle(data)
        return data

if __name__ == '__main__':
    data_path = '/home/fanfanfeng/working_data/nlp_data/similary/senteval_cn/LCQMC/LCQMC.valid.data'
    print(LCQMC.load_data(data_path))