from typing import Tuple, List
import glob
import os
from tqdm import tqdm
from nlp_tools.generators import ABCGenerator

class AutoTitleThunc(ABCGenerator):
    __corpus_name__ = 'thunc_text_summarization'

    def __init__(self,file_path,shuffle: bool = True,buffer_size: int = 5000):
        self.file_path = file_path
        self.shufflle = shuffle
        super(AutoTitleThunc, self).__init__(buffer_size=buffer_size)

    def __iter__(self):

        golb_file_path = os.path.join(self.file_path,"*/*.txt")
        txts = glob.glob(golb_file_path)


        for txt in tqdm(txts):
            text = open(txt, encoding='utf-8').read()
            text = text.split('\n')
            if len(text) > 1:
                title = text[0]
                content = '\n'.join(text[1:])
                yield content,title
                #titles.append(title)
                #contexts.append(content)
       # return contexts,titles

    def __len__(self) -> int:
        return 890000


    def load_data(self):

        golb_file_path = os.path.join(self.file_path,"*/*.txt")
        txts = glob.glob(golb_file_path)

        titles = []
        contexts = []
        count = 0
        for txt in tqdm(txts):
            text = open(txt, encoding='utf-8').read()
            text = text.split('\n')
            if len(text) > 1:
                title = text[0]
                content = '\n'.join(text[1:])
                titles.append(title)
                contexts.append(content)

            count += 1

        return contexts,titles