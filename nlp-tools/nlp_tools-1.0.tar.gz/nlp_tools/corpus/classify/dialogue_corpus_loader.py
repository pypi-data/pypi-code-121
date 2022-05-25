import pandas as pd
from nlp_tools import utils
import re


class DialogueCorpusLoader():
    __name__ ="dialogue_corpus_loader"
    def __init__(self,**kwargs):
        pass

    @classmethod
    def load_data(cls,data_path, shuffle: bool = True):
        df = pd.read_csv(data_path)
        sentences = df["data"].tolist()
        labels = df['label'].tolist()

        sentences_cut = []

        for sen in sentences:
            #sen = sen.replace("$","")
            sen_cut_list = sen.split("\n")
            sen_cut_list = [item for item in sen_cut_list if item != ""]

            sen_cut_list = [ re.sub("^.{0,1}\:","",sub_sen) for sub_sen in sen_cut_list]
            sentences_cut.append(sen_cut_list)

        if shuffle:
            sentences_cut, labels = utils.unison_shuffled_copies(sentences_cut, labels)

        data_union = [(x, y) for x, y in zip(sentences_cut, labels)]
        return data_union


if __name__ == '__main__':
    DialogueCorpusLoader.load_data("/home/fanfanfeng/working_data/nlp_data/working/classify/train.csv")







